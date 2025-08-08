import stripe
import os
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.payment import bp
from app.models import User, Subscription

# Stripe API key should be set in your environment
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

@bp.route('/subscribe')
@login_required
def subscribe():
    """Renders the subscription page."""
    # This page could have details about the subscription plan
    return render_template('payment/subscribe.html')

@bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Creates a Stripe Checkout session."""
    price_id = os.environ.get('STRIPE_PRICE_ID')
    if not price_id or not stripe.api_key:
        flash('Payment system is not configured. Please contact support.', 'danger')
        return redirect(url_for('main.index'))

    try:
        # Create a new Stripe Customer if one doesn't exist
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=current_user.name,
                metadata={'user_id': current_user.id}
            )
            current_user.stripe_customer_id = customer.id
            db.session.commit()

        checkout_session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            success_url=url_for('payment.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('payment.cancel', _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        current_app.logger.error(f"Stripe Error: {e}")
        flash(f'An error occurred: {e}', 'danger')
        return redirect(url_for('payment.subscribe'))

@bp.route('/success')
@login_required
def success():
    """Success page after payment."""
    # Here you should ideally verify the session and fulfill the purchase,
    # but the webhook is a more reliable way to do this.
    flash('Thank you for your payment! Your subscription is being activated.', 'success')
    return render_template('payment/success.html')

@bp.route('/cancel')
@login_required
def cancel():
    """Cancellation page."""
    flash('Your payment was cancelled. You have not been charged.', 'info')
    return render_template('payment/cancel.html')

@bp.route('/webhook', methods=['POST'])
def webhook():
    """Stripe webhook handler."""
    event = None
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature', None)
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

    if not sig_header or not webhook_secret:
        # Configuration error
        return 'Webhook secret not configured', 400

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        current_app.logger.warning(f"Webhook payload error: {e}")
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        current_app.logger.warning(f"Webhook signature error: {e}")
        return 'Invalid signature', 400

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_id = session.get('customer')
        subscription_id = session.get('subscription')

        # Find user by stripe_customer_id
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            # Retrieve subscription details to get period dates
            sub_data = stripe.Subscription.retrieve(subscription_id)
            from datetime import datetime

            new_subscription = Subscription(
                user_id=user.id,
                stripe_customer_id=customer_id,
                stripe_subscription_id=subscription_id,
                status=sub_data.status,
                current_period_start=datetime.fromtimestamp(sub_data.current_period_start),
                current_period_end=datetime.fromtimestamp(sub_data.current_period_end)
            )
            db.session.add(new_subscription)
            db.session.commit()
            current_app.logger.info(f"New subscription created for user {user.id}")

    elif event['type'] in ['customer.subscription.updated', 'customer.subscription.deleted']:
        sub_data = event['data']['object']
        subscription_id = sub_data.id

        subscription = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
        if subscription:
            from datetime import datetime
            subscription.status = sub_data.status
            subscription.current_period_start = datetime.fromtimestamp(sub_data.current_period_start)
            subscription.current_period_end = datetime.fromtimestamp(sub_data.current_period_end)
            db.session.commit()
            current_app.logger.info(f"Subscription {subscription_id} updated to status {sub_data.status}")

    else:
        current_app.logger.info(f"Unhandled Stripe event type: {event['type']}")

    return 'Success', 200

@bp.route('/customer-portal')
@login_required
def customer_portal():
    """Redirects to the Stripe Customer Portal."""
    if not current_user.stripe_customer_id:
        flash('You do not have a subscription to manage.', 'warning')
        return redirect(url_for('main.index'))

    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=url_for('main.index', _external=True)
        )
        return redirect(portal_session.url, code=303)
    except Exception as e:
        current_app.logger.error(f"Stripe Portal Error: {e}")
        flash('Could not connect to the customer portal. Please try again later.', 'danger')
        return redirect(url_for('main.index'))
