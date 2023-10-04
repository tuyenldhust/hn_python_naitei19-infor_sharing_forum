from typing import Any
from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """
    Model custom more information for user
    """
    achievement = models.IntegerField(verbose_name=_('Thành tích'), choices=(
        (5, _('Kim cương')),
        (4, _('Bạch kim')),
        (3, _('Vàng')),
        (2, _('Bạc')),
        (1, _('Đồng')),
        (0, _('Chưa có thành tích'))
    ), default=0)
    point = models.IntegerField(
        verbose_name=_('Điểm'),
        default=0)
    avatar_link = models.CharField(
        verbose_name=_('Link ảnh đại diện'),
        max_length=1024,
        default="/static/user_layout/images/default-avatar.jpg")
    phone = models.CharField(
        verbose_name=_('Số điện thoại'),
        max_length=10,
        default="")
    count_violated = models.IntegerField(
        verbose_name=_('Số lần vi phạm'),
        default=0)
    time_banned = models.DateTimeField(
        verbose_name=_('Thời gian bị cấm'),
        null=True,
        blank=True)
    is_deleted = models.BooleanField(
        verbose_name=_('Trạng thái xóa'),
        default=False)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.username

    def delete(self, using=None, keep_parents=False):
        """
        Override delete method
        """
        self.is_deleted = True
        self.save()
        return 1, {'is_deleted': 1}


class ReportUser(models.Model):
    """
    Model representing a report user
    """
    reporter = models.ForeignKey(
        verbose_name=_('Người báo cáo'),
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='reporter')
    reported_user = models.ForeignKey(
        verbose_name=_('Người bị báo cáo'),
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='reported_user')
    reason = models.CharField(
        verbose_name=_('Lý do'),
        max_length=1024)
    time = models.DateTimeField(
        verbose_name=_('Thời gian báo cáo'),
        auto_now_add=True)
    is_resolved = models.BooleanField(
        verbose_name=_('Trạng thái giải quyết'),
        default=False,
        choices=((True, 'Resolved'), (False, 'Not resolved')))

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.reporter.username + " reported " + self.reported_user.username + " for " + self.reason


class Follow(models.Model):
    """
    Model representing a follow
    """
    follower = models.ForeignKey(
        verbose_name=_('Người theo dõi'),
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='follower')
    followed = models.ForeignKey(
        verbose_name=_('Người được theo dõi'),
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='followed')
    time = models.DateTimeField(
        verbose_name=_('Thời gian theo dõi'),
        auto_now_add=True)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.follower.username + " followed " + self.followed.username


class Post(models.Model):
    """
    Model representing a post
    """
    user = models.ForeignKey(
        verbose_name=_('Người đăng'),
        to=CustomUser,
        on_delete=models.CASCADE)
    title = models.CharField(
        verbose_name=_('Tiêu đề'),
        max_length=255)
    categories = models.ManyToManyField(
        verbose_name=_('Chuyên mục'),
        to='Category')
    hashtags = models.ManyToManyField(
        verbose_name=_('Hashtag'),
        to='HashTag',
        blank=True,
        null=True)
    content = RichTextField(
        verbose_name=_('Nội dung'),
    )
    mode = models.IntegerField(
        verbose_name=_('Chế độ'),
        default=0,
        choices=((0, _('Public')), (1, _('Private'))))
    status = models.IntegerField(
        verbose_name=_('Trạng thái'),
        default=0, 
        choices=
            ((0, _('Draft')), (1, _('Normal')),
            (2, _('Deleted')), (3, _('Banned')),
            (4, _('Waiting for approval')), (5, _('Rejected'))))
    created_at = models.DateTimeField(
        verbose_name=_('Ngày đăng'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name=_('Ngày cập nhật'),
        auto_now=True
    )
    view_count = models.IntegerField(
        verbose_name=_('Lượt xem'),
        default=0
    )
    is_deteted = models.BooleanField(
        verbose_name=_('Đã xóa'),
        default=False
    )

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.user.username + " posted " + self.title


class Category(models.Model):
    """
    Model representing a category
    """
    name = models.CharField(
        verbose_name=_('Tên chuyên mục'),
        max_length=255
    )

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.name
    
    class Meta:
        verbose_name = 'Chuyên mục'
        verbose_name_plural = 'Chuyên mục'


class HashTag(models.Model):
    """
    Model representing a hashtag
    """
    name = models.CharField(
        verbose_name=_('Tên hashtag'),
        max_length=255
    )

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.name


class PostPaid(models.Model):
    """
    Model representing a post paid
    """
    user = models.ForeignKey(
        verbose_name=_('Người thanh toán'),
        to=CustomUser,
        on_delete=models.CASCADE)
    post = models.ForeignKey(
        verbose_name=_('Bài viết'),
        to=Post,
        on_delete=models.CASCADE)
    time = models.DateTimeField(
        verbose_name=_('Thời gian thanh toán'),
        auto_now_add=True)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.user.username + " paid for " + self.post.title


class PostReaction(models.Model):
    """
    Model representing a post reaction
    """
    user = models.ForeignKey(
        verbose_name=_('Người Vote'),
        to=CustomUser,
        on_delete=models.CASCADE)
    post = models.ForeignKey(
        verbose_name=_('Bài viết'),
        to=Post, 
        on_delete=models.CASCADE)
    feedback_value = models.IntegerField(
        verbose_name=_('Vote'),
        choices=((1, 'Upvote'), (-1, 'Downvote')))
    time = models.DateTimeField(
        verbose_name=_('Thời gian vote'),
        auto_now_add=True)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.user.username + " reacted " + self.post.title


class ReportPost(models.Model):
    """
    Model representing a report post
    """
    reporter = models.ForeignKey(
        verbose_name=_('Người báo cáo'),
        to=CustomUser, 
        on_delete=models.CASCADE,
        related_name='reporter_post')
    reported_post = models.ForeignKey(
        verbose_name=_('Bài viết bị báo cáo'),
        to=Post,
        on_delete=models.CASCADE,
        related_name='reported_post')
    reason = models.CharField(
        verbose_name=_('Lý do'),
        max_length=1024)
    time = models.DateTimeField(
        verbose_name=_('Thời gian báo cáo'),
        auto_now_add=True)
    is_resolved = models.BooleanField(
        verbose_name=_('Trạng thái giải quyết'),
        default=False,
        choices=((True, _('Resolved')), (False, _('Not resolved'))))

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.reporter.username + " reported " + self.reported_post.title + " for " + self.reason


class Comment(models.Model):
    """
    Model representing a comment
    """
    user = models.ForeignKey(
        verbose_name=_('Người bình luận'),
        to=CustomUser,
        on_delete=models.CASCADE)
    post = models.ForeignKey(
        verbose_name=_('Bài viết'),
        to=Post,
        on_delete=models.CASCADE)
    parent = models.ForeignKey(
        verbose_name=_('Bình luận cha'),
        to='self',
        on_delete=models.CASCADE,
        default=None,
        null=True)
    content = models.CharField(
        verbose_name=_('Nội dung'),
        max_length=10000)
    is_edited = models.BooleanField(
        verbose_name=_('Đã chỉnh sửa'),
        default=False)
    updated_at = models.DateTimeField(
        verbose_name=_('Ngày chỉnh sửa'),
        auto_now=True)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.user.username + " commented " + self.post.title


class Bookmark(models.Model):
    """
    Model representing a bookmark
    """
    user = models.ForeignKey(
        verbose_name=_('Người bookmark'),
        to=CustomUser,
        on_delete=models.CASCADE)
    post = models.ForeignKey(
        verbose_name=_('Bài viết'),
        to=Post,
        on_delete=models.CASCADE)
    time = models.DateTimeField(
        verbose_name=_('Thời gian bookmark'),
        auto_now_add=True)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.user.username + " bookmarked " + self.post.title


class Notification(models.Model):
    """
    Model representing a notification
    """
    receive_user = models.ForeignKey(
        verbose_name=_('Người nhận'),
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='receive_user')
    action_user = models.ForeignKey(
        verbose_name=_('Người thực hiện'),
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='action_user')
    content = models.CharField(
        verbose_name=_('Nội dung'),
        max_length=1000,
        help_text=_('Nội dung thông báo chứa id post hoặc id comment hoặc id reply comment'))
    type_notify = models.IntegerField(
        verbose_name=_('Loại thông báo'),
        choices=(
            (0, _('Like_post')),
            (1, _('Comment')),  
            (2, _('Reply_comment'))))
    is_read = models.BooleanField(
        verbose_name=_('Đã đọc'),
        default=False)
    time = models.DateTimeField(
        verbose_name=_('Thời gian nhận'),
        auto_now_add=True)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.user.username + " got notification " + self.content
