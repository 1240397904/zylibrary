from django.contrib import admin

# Register your models here.
from django.utils import timezone
from django.utils.html import format_html
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from . import models

admin.site.site_header = '***********图书管理**********'
admin.site.site_title = '。。。。。图书管理。。。。。'
admin.site.index_title = 'home'


def update_enabled(admin_model, request, queryset):
    """批量启用动作"""
    queryset.update(status=2)


def update_disabled(admin_model, request, queryset):
    """批量禁用动作"""
    queryset.update(status=-2)


update_enabled.short_description = '批量有效'
update_disabled.short_description = '批量无效'


class BaseAdmin(admin.ModelAdmin):
    """后台管理统一父类"""

    list_filter = ('status',)
    # 将动作函数添加到动作列表中
    actions = (update_enabled, update_disabled)

    def save_model(self, request, obj, form, change):
        if change:
            obj.update_user_id = request.user.id
            obj.update_time = timezone.now()
        else:
            obj.create_user_id = request.user.id
            obj.create_time = timezone.now()

        super().save_model(request, obj, form, change)


@admin.register(models.Category)
class CategoryAdmin(BaseAdmin):
    """分类管理"""

    site_order = 1
    list_display = ('name', 'desc', 'order_number', 'status')
    fields = ('name', 'desc', 'order_number', 'status')


@admin.register(models.Shelf)
class ShelfAdmin(BaseAdmin):
    """书架管理"""

    site_order = 2
    list_display = ('code', 'location', 'category', 'floors', 'capacity', 'status')
    fields = ('code', 'location', 'category', 'floors', 'capacity', 'status')


def cover(obj):
    return format_html(
        '<img src="%s%s" onerror="this.src=\'%sbook.png\'" style="max-height:100px; max-width:100px">' %
        (settings.MEDIA_URL, obj.cover, settings.MEDIA_URL))


cover.short_description = '封面'


@admin.register(models.Book)
class BookAdmin(BaseAdmin):
    """图书管理"""
    site_order = 3
    list_display = ('name', cover, 'author', 'press', 'category', 'shelf', 'shelf_floor', 'score', 'status')
    list_filter = ('status', 'category')
    search_fields = ('name', 'author', 'press')

    fieldsets = (
        (
            None,
            {
                'fields': ('name', 'version', 'author', 'trans', 'press', 'ISBN', 'total_page',
                           'price', 'real_price', 'cover', 'category', 'shelf', 'shelf_floor', 'book_status', 'status')
            }
        ),
        (
            'Other Options',
            {
                'classes': ('collapse',),
                'fields': ('series', 'series_number'),
                'description': '系列书籍的设置'
            }
        ),
    )


def fullname(obj):
    user = None
    if isinstance(obj, models.UserProfile) and obj.user:
        user = obj.user
    elif obj.user_profile and obj.user_profile.user:
        user = obj.user_profile.user
    if user:
        if user.first_name and user.last_name:
            return user.last_name + user.first_name
        else:
            return user.username
    return '未知'


fullname.short_description = _('Fullname')


@admin.register(models.CheckOut)
class CheckOutAdmin(admin.ModelAdmin):
    """借阅管理"""

    site_order = 4
    list_filter = ('type',)
    list_display = ('user_profile', fullname, 'book', 'time', 'type', 'return_date', 'returned_time', 'allow_shift')
    fields = ('user_profile', 'book', 'time', 'type', 'return_date', 'returned_time', 'allow_shift')
    autocomplete_fields = ['book']
    search_fields = ('user_profile', 'book')


@admin.register(models.Comment)
class CommentAdmin(BaseAdmin):
    """书评管理"""

    site_order = 5
    list_display = ('checkout', 'score', 'content', 'status')
    fields = ('checkout', 'score', 'content', 'status')
    autocomplete_fields = ('checkout',)


@admin.register(models.Note)
class NoteAdmin(BaseAdmin):
    """笔记管理"""

    site_order = 6
    list_display = ('checkout', 'page', 'content', 'status')
    fields = ('checkout', 'page', 'content', 'status')
    autocomplete_fields = ('checkout',)


@admin.register(models.Rent)
class RentAdmin(admin.ModelAdmin):
    """租阅管理"""

    site_order = 7
    list_filter = ('pay_status',)
    list_display = ('checkout', 'days', 'amount', 'pay_status')
    fields = ('checkout', 'days', 'amount', 'order_no', 'trade_no', 'pay_status')
    autocomplete_fields = ('checkout',)


@admin.register(models.Shift)
class ShiftAdmin(admin.ModelAdmin):
    """转借管理"""

    site_order = 8
    list_filter = ('shift_status',)
    list_display = ('checkout', 'request_user_profile', 'agreed', 'shift_status', 'request_time')
    fields = ('checkout', 'request_user_profile', 'reason', 'agreed', 'reply', 'shift_status',
              'request_time', 'reply_time', 'complete_time')
    autocomplete_fields = ('checkout', 'request_user_profile')


def avatar(obj):
    return format_html('<img src="%s%s" onerror="this.src=\'%suser.png\'" '
                       'style="max-height:85px; max-width:85px; border-radius:50%%;">' %
                       (settings.MEDIA_URL, obj.avatar, settings.MEDIA_URL))


avatar.short_description = _('Avatar')


@admin.register(models.UserProfile)
class UserProfileAdmin(BaseAdmin):
    """用户资料管理"""

    site_order = 10
    list_display = (avatar, 'user', fullname, 'mobile', 'sex', 'job', 'start_date', 'end_date', 'status')
    fields = ('user', 'mobile', 'sex', 'birth', 'job', 'avatar', 'start_date', 'end_date', 'status')
    autocomplete_fields = ('user',)
    search_fields = ('user',)


