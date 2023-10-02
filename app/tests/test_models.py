from django.test import TestCase
from django.utils import timezone
from app.models import *
from django.utils.translation import gettext_lazy as _

class CustomUserTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass',
            achievement=3,
            point=100,
            avatar_link='/static/user_layout/images/test-avatar.jpg',
            phone='0123456789',
            count_violated=2,
            time_banned=timezone.now(),
            is_deleted=False
        )

    def test_string_representation(self):
        self.assertEqual(str(self.user), 'testuser')

    def test_delete_method(self):
        self.user.delete(using='default', keep_parents=False)
        self.assertTrue(self.user.is_deleted)

    def test_default_achievement(self):
        user = CustomUser.objects.create_user(
            username='testuser2',
            password='testpass'
        )
        self.assertEqual(user.achievement, 0)

    def test_default_avatar_link(self):
        user = CustomUser.objects.create_user(
            username='testuser3',
            password='testpass'
        )
        self.assertEqual(user.avatar_link, '/static/user_layout/images/default-avatar.jpg')

    def test_default_phone(self):
        user = CustomUser.objects.create_user(
            username='testuser4',
            password='testpass'
        )
        self.assertEqual(user.phone, '')

    def test_default_count_violated(self):
        user = CustomUser.objects.create_user(
            username='testuser5',
            password='testpass'
        )
        self.assertEqual(user.count_violated, 0)

    def test_default_time_banned(self):
        user = CustomUser.objects.create_user(
            username='testuser6',
            password='testpass'
        )
        self.assertIsNone(user.time_banned)

    def test_default_is_deleted(self):
        user = CustomUser.objects.create_user(
            username='testuser7',
            password='testpass'
        )
        self.assertFalse(user.is_deleted)

class ReportUserTestCase(TestCase):
    def setUp(self):
        self.reporter = CustomUser.objects.create_user(
            username='testuser1',
            password='testpass1'
        )
        self.reported_user = CustomUser.objects.create_user(
            username='testuser2',
            password='testpass2'
        )
        self.report = ReportUser.objects.create(
            reporter=self.reporter,
            reported_user=self.reported_user,
            reason='Test reason',
            time=timezone.now(),
            is_resolved=False
        )

    def test_string_representation(self):
        self.assertEqual(str(self.report), 'testuser1 reported testuser2 for Test reason')

    def test_default_is_resolved(self):
        report = ReportUser.objects.create(
            reporter=self.reporter,
            reported_user=self.reported_user,
            reason='Test reason 2',
            time=timezone.now()
        )
        self.assertFalse(report.is_resolved)

    def test_reporter_foreign_key(self):
        self.assertEqual(self.report.reporter, self.reporter)

    def test_reported_user_foreign_key(self):
        self.assertEqual(self.report.reported_user, self.reported_user)

class FollowTestCase(TestCase):
    def setUp(self):
        self.follower = CustomUser.objects.create_user(
            username='testuser1',
            password='testpass1'
        )
        self.followed = CustomUser.objects.create_user(
            username='testuser2',
            password='testpass2'
        )
        self.follow = Follow.objects.create(
            follower=self.follower,
            followed=self.followed,
            time=timezone.now()
        )

    def test_string_representation(self):
        self.assertEqual(str(self.follow), 'testuser1 followed testuser2')

    def test_follower_foreign_key(self):
        self.assertEqual(self.follow.follower, self.follower)

    def test_followed_foreign_key(self):
        self.assertEqual(self.follow.followed, self.followed)

class PostTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.category = Category.objects.create(
            name='Test category'
        )
        self.hashtag = HashTag.objects.create(
            name='testhashtag'
        )
        self.post = Post.objects.create(
            user=self.user,
            title='Test post',
            content='Test content',
            mode=0,
            status=1,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            view_count=0,
            is_deteted=False
        )
        self.post.categories.add(self.category)
        self.post.hashtags.add(self.hashtag)

    def test_string_representation(self):
        self.assertEqual(str(self.post), 'testuser posted Test post')

    def test_default_view_count(self):
        post = Post.objects.create(
            user=self.user,
            title='Test post 2',
            content='Test content 2',
            mode=0,
            status=1,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            is_deteted=False
        )
        self.assertEqual(post.view_count, 0)

    def test_default_is_deleted(self):
        post = Post.objects.create(
            user=self.user,
            title='Test post 3',
            content='Test content 3',
            mode=0,
            status=1,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            view_count=0
        )
        self.assertFalse(post.is_deteted)

    def test_category_many_to_many_relationship(self):
        self.assertEqual(self.post.categories.first(), self.category)

    def test_hashtag_many_to_many_relationship(self):
        self.assertEqual(self.post.hashtags.first(), self.hashtag)

class CategoryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Category.objects.create(name='Test Category')
        cls.category_id = Category.objects.get(name='Test Category').id

    def test_name_label(self):
        category = Category.objects.get(id=self.category_id)
        field_label = category._meta.get_field('name').verbose_name
        self.assertEquals(field_label, 'Tên chuyên mục')

    def test_name_max_length(self):
        category = Category.objects.get(id=self.category_id)
        max_length = category._meta.get_field('name').max_length
        self.assertEquals(max_length, 255)

    def test_object_name_is_name(self):
        category = Category.objects.get(id=self.category_id)
        expected_object_name = category.name
        self.assertEquals(expected_object_name, str(category))

    def test_delete_sets_is_deleted_true(self):
        category = Category.objects.get(id=self.category_id)
        category.delete()
        self.assertFalse(Category.objects.filter(id=self.category_id).exists())

class HashTagModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        HashTag.objects.create(name='Test Hashtag')
        cls.hashtag_id = HashTag.objects.get(name='Test Hashtag').id

    def test_name_label(self):
        hashtag = HashTag.objects.get(id=self.hashtag_id)
        field_label = hashtag._meta.get_field('name').verbose_name
        self.assertEquals(field_label, 'Tên hashtag')

    def test_name_max_length(self):
        hashtag = HashTag.objects.get(id=self.hashtag_id)
        max_length = hashtag._meta.get_field('name').max_length
        self.assertEquals(max_length, 255)

    def test_object_name_is_name(self):
        hashtag = HashTag.objects.get(id=self.hashtag_id)
        expected_object_name = hashtag.name
        self.assertEquals(expected_object_name, str(hashtag))

class PostPaidModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass'
        )
        cls.post = Post.objects.create(
            user=cls.user,
            title='Test post',
            content='Test content',
            mode=0,
            status=1,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            view_count=0,
            is_deteted=False
        )
        cls.post_paid = PostPaid.objects.create(
            user=cls.user,
            post=cls.post,
            time=timezone.now()
        )

    def test_string_representation(self):
        expected_string = f'{self.user.username} paid for {self.post.title}'
        self.assertEqual(str(self.post_paid), expected_string)

    def test_user_foreign_key(self):
        self.assertEqual(self.post_paid.user, self.user)

    def test_post_foreign_key(self):
        self.assertEqual(self.post_paid.post, self.post)

class PostReactionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass'
        )
        cls.post = Post.objects.create(
            user=cls.user,
            title='Test post',
            content='Test content',
            mode=0,
            status=1,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            view_count=0,
            is_deteted=False
        )
        cls.post_reaction = PostReaction.objects.create(
            user=cls.user,
            post=cls.post,
            feedback_value=1,
            time=timezone.now()
        )

    def test_string_representation(self):
        expected_string = f'{self.user.username} reacted {self.post.title}'
        self.assertEqual(str(self.post_reaction), expected_string)

    def test_user_foreign_key(self):
        self.assertEqual(self.post_reaction.user, self.user)

    def test_post_foreign_key(self):
        self.assertEqual(self.post_reaction.post, self.post)

    def test_feedback_value_choices(self):
        self.assertIn(self.post_reaction.feedback_value, [-1, 1])

    def test_time_auto_now_add(self):
        self.assertIsNotNone(self.post_reaction.time)

class ReportPostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.reporter = CustomUser.objects.create_user(
            username='testuser1',
            password='testpass1'
        )
        cls.reported_post = Post.objects.create(
            user=cls.reporter,
            title='Test post',
            content='Test content',
            mode=0,
            status=1,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            view_count=0,
            is_deteted=False
        )
        cls.report_post = ReportPost.objects.create(
            reporter=cls.reporter,
            reported_post=cls.reported_post,
            reason='Test reason',
            time=timezone.now(),
            is_resolved=False
        )

    def test_string_representation(self):
        expected_string = f'{self.reporter.username} reported {self.reported_post.title} for {self.report_post.reason}'
        self.assertEqual(str(self.report_post), expected_string)

    def test_reporter_foreign_key(self):
        self.assertEqual(self.report_post.reporter, self.reporter)

    def test_reported_post_foreign_key(self):
        self.assertEqual(self.report_post.reported_post, self.reported_post)

    def test_reason_max_length(self):
        max_length = self.report_post._meta.get_field('reason').max_length
        self.assertEquals(max_length, 1024)

    def test_is_resolved_default_false(self):
        self.assertFalse(self.report_post.is_resolved)

    def test_is_resolved_choices(self):
        choices = self.report_post._meta.get_field('is_resolved').choices
        self.assertEquals(choices, ((True, _('Resolved')), (False, _('Not resolved'))))

class CommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass'
        )
        cls.post = Post.objects.create(
            user=cls.user,
            title='Test post',
            content='Test content',
            mode=0,
            status=1,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            view_count=0,
            is_deteted=False
        )
        cls.comment = Comment.objects.create(
            user=cls.user,
            post=cls.post,
            parent=None,
            content='Test comment',
            is_edited=False,
            updated_at=timezone.now()
        )

    def test_string_representation(self):
        expected_string = f'{self.user.username} commented {self.post.title}'
        self.assertEqual(str(self.comment), expected_string)

    def test_user_foreign_key(self):
        self.assertEqual(self.comment.user, self.user)

    def test_post_foreign_key(self):
        self.assertEqual(self.comment.post, self.post)

    def test_parent_foreign_key(self):
        self.assertIsNone(self.comment.parent)

    def test_content_max_length(self):
        max_length = self.comment._meta.get_field('content').max_length
        self.assertEquals(max_length, 10000)

    def test_is_edited_default_false(self):
        self.assertFalse(self.comment.is_edited)

    def test_updated_at_auto_now(self):
        self.assertIsNotNone(self.comment.updated_at)

class BookmarkModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass'
        )
        cls.post = Post.objects.create(
            user=cls.user,
            title='Test post',
            content='Test content',
            mode=0,
            status=1,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            view_count=0,
            is_deteted=False
        )
        cls.bookmark = Bookmark.objects.create(
            user=cls.user,
            post=cls.post,
            time=timezone.now()
        )

    def test_string_representation(self):
        expected_string = f'{self.user.username} bookmarked {self.post.title}'
        self.assertEqual(str(self.bookmark), expected_string)

    def test_user_foreign_key(self):
        self.assertEqual(self.bookmark.user, self.user)

    def test_post_foreign_key(self):
        self.assertEqual(self.bookmark.post, self.post)

    def test_time_auto_now_add(self):
        self.assertIsNotNone(self.bookmark.time)

class NotificationModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass'
        )
        cls.notification = Notification.objects.create(
            user=cls.user,
            content='Test notification',
            is_read=False,
            time=timezone.now()
        )

    def test_string_representation(self):
        expected_string = f'{self.user.username} got notification {self.notification.content}'
        self.assertEqual(str(self.notification), expected_string)

    def test_user_foreign_key(self):
        self.assertEqual(self.notification.user, self.user)

    def test_content_max_length(self):
        max_length = self.notification._meta.get_field('content').max_length
        self.assertEquals(max_length, 1000)

    def test_is_read_default_false(self):
        self.assertFalse(self.notification.is_read)

    def test_time_auto_now_add(self):
        self.assertIsNotNone(self.notification.time)
