from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.videos import bp
from app.models import Video

@bp.route('/')
@login_required
def video_list():
    """Displays a list of all videos."""
    videos = Video.query.order_by(Video.published_at.desc()).all()
    return render_template('videos/video_list.html', videos=videos, title='Videos')

@bp.route('/<uuid:video_id>')
@login_required
def video_detail(video_id):
    """Displays the page for a single video."""
    # Check for active subscription
    if not current_user.has_active_subscription():
        flash('You need an active subscription to watch videos.', 'warning')
        return redirect(url_for('payment.subscribe'))

    video = Video.query.get_or_404(video_id)
    return render_template('videos/video_detail.html', video=video, title=video.title)
