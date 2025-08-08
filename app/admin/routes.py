from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.admin import bp
from app.admin.decorators import admin_required
from app.admin.forms import VideoForm
from app.models import Video, User

@bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard."""
    users = User.query.all()
    videos = Video.query.all()
    return render_template('admin/dashboard.html', users=users, videos=videos, title="Admin Dashboard")

@bp.route('/videos/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_video():
    """Add a new video."""
    form = VideoForm()
    if form.validate_on_submit():
        video = Video(
            title=form.title.data,
            description=form.description.data,
            vimeo_id=form.vimeo_id.data,
            vimeo_hash=form.vimeo_hash.data,
            is_public=form.is_public.data
        )
        db.session.add(video)
        db.session.commit()
        flash('New video has been added.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/video_form.html', form=form, title="Add Video")

@bp.route('/videos/edit/<uuid:video_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_video(video_id):
    """Edit an existing video."""
    video = Video.query.get_or_404(video_id)
    form = VideoForm(obj=video)
    if form.validate_on_submit():
        video.title = form.title.data
        video.description = form.description.data
        video.vimeo_id = form.vimeo_id.data
        video.vimeo_hash = form.vimeo_hash.data
        video.is_public = form.is_public.data
        db.session.commit()
        flash('The video has been updated.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/video_form.html', form=form, title="Edit Video", video=video)
