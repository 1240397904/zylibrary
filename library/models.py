from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
# Create your models here.


class Base(models.Model):
    """模型父类"""
    STATUS = (
        (2, '有效'),
        (-2, '无效'),
    )
    status = models.IntegerField('状态', default=2, choices=STATUS)
    create_user_id = models.IntegerField('创建用户', null=True, editable=False)
    create_time = models.DateTimeField('新建时间', default=timezone.now, editable=False)
    update_user_id = models.IntegerField('更新用户', null=True, editable=False)
    update_time = models.DateTimeField('更新时间', default=timezone.now, editable=False)

    class Meta:
        abstract = True


class Category(Base):
    """图书分类"""
    name = models.CharField('名字', max_length=20, null=False)
    desc = models.CharField('描述', max_length=100)
    order_number = models.IntegerField('编号', default=0)

    class Meta:
        verbose_name = '种类'
        verbose_name_plural = '种类'
        ordering = ['-status', 'order_number']

    def __repr__(self):
        return '<Category {id: %s, name: %s}>' % (self.id, self.name)

    def __str__(self):
        return self.name


class Shelf(Base):
    """书架"""

    category = models.ForeignKey('Category', on_delete=models.DO_NOTHING, null=True, verbose_name='种类')
    code = models.CharField('书架号', max_length=10, null=False)
    location = models.CharField('位置', max_length=20, null=False, default='')
    floors = models.IntegerField('层数', default=4)
    capacity = models.IntegerField('书的数量', default=100)

    class Meta:
        verbose_name ='书架'
        verbose_name_plural = '书架'

    def __repr__(self):
        return '<Shelf {id: %s, code: %s, location: %s}>' % (self.id, self.code, self.location)

    def __str__(self):
        return self.code


class BookImageStorage(FileSystemStorage):
    """处理图书封面图片"""

    def _save(self, name, content):
        filename = super()._save(name, content)
        path = self.path(name)
        from PIL import Image
        img = Image.open(path)
        img.thumbnail([240, 240])
        img.save(path)
        return filename


class Book(Base):
    """图书"""

    BOOK_STATUS = (
        ('ON', '在架'),
        ('OUT', '借出'),
        ('RE', '归还'),
        ('LO', '丢失')
    )

    name = models.CharField('名字', max_length=20, null=False)
    version = models.CharField('版本', max_length=10, default='', blank=True)
    author = models.CharField('作者', max_length=20, null=False)
    trans = models.CharField('翻译者', max_length=50, default='', blank=True)
    press = models.CharField('出版社', max_length=20, null=False)
    ISBN = models.CharField('国际标准图书编号', max_length=20, null=False)
    total_page = models.IntegerField('总页数', default=200)
    price = models.DecimalField('价格', default=50.00, max_digits=10, decimal_places=2)
    real_price = models.DecimalField('售价', default=40.00, max_digits=10, decimal_places=2)
    cover = models.ImageField('封面', blank=True, upload_to='book', storage=BookImageStorage(), null=True)
    score = models.FloatField('评分', default=4.0, editable=False)
    category = models.ForeignKey(Category, verbose_name=' 种类', on_delete=models.DO_NOTHING, null=True)
    shelf = models.ForeignKey(Shelf, verbose_name='书架', on_delete=models.CASCADE, null=True)
    shelf_floor = models.IntegerField('书架层数', default=1)
    book_status = models.CharField('书的状态', choices=BOOK_STATUS, default='在架', null=False, max_length=10)
    series = models.CharField('系列', max_length=20, default='', blank=True)
    series_number = models.IntegerField('系列数', default=0)

    class Meta:
        verbose_name = '书名'
        verbose_name_plural = '书名'
        ordering = ['-status', '-score']

    # def __repr__(self):
    #     return '<Book {id: %s, name: %s, author: %s}>' % (self.id, self.name, self.author)

    def __str__(self):
        return self.name


def calc_end_date(*args, **kwargs):
    """计算失效期"""

    now = timezone.now()
    m6 = timezone.timedelta(days=31 * 6)
    return now + m6


class UserStorage(FileSystemStorage):
    """处理用户头像"""
    def _save(self, name, content):
        filename = super()._save(name, content)

        path = self.path(name)
        from PIL import Image
        img = Image.open(path)

        left = top = right = bottom = 0
        if img.width > img.height:
            left = (img.width - img.height)/2
            right = left + img.height
            bottom = img.height
        else:
            top = (img.height - img.width) / 2
            bottom = top + img.width
            right = img.width
        img.crop((left, top, right, bottom)).resize((200, 200), resample=Image.BICUBIC).save(path)
        return filename


class UserProfile(Base):
    """用户资料"""
    SEX = (
        ('M', '男'),
        ('N', '女')
    )

    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, null=True, verbose_name='用户')
    mobile = models.CharField('电话号', max_length=11, default='', blank=True)
    sex = models.CharField('性别', choices=SEX, max_length=1, default='M', null=False)
    birth = models.DateField('出生日期', null=True, blank=True)
    avatar = models.ImageField('头像', upload_to='user', blank=True, storage=UserStorage(), null=True)
    job = models.CharField('职业', max_length=20, default='', blank=True)
    start_date = models.DateField('开始日期', default=timezone.now)
    end_date = models.DateField('结束日期', default=calc_end_date)
    wx_id = models.CharField('微信号', max_length=100, default='', editable=False)

    class Meta:
        verbose_name = '用户配置文件'
        verbose_name_plural = '用户配置文件'

    def __repr__(self):
        return '<UserProfile {id: %s, mobile: %s}>' % (self.id, self.mobile)

    def __str__(self):
        return self.user.username if self.user else self.mobile


def calc_return_date():
    """计算还书日期"""

    now = timezone.now()
    days_15 = timezone.timedelta(days=15)
    return now + days_15


class CheckOut(Base):
    """借阅"""

    TYPE = (
        ('SC', _('Scan Code')),
        ('SH', _('Shift')),
    )
    BOOK_STATUS = (
        ('ON', _('On Shelf')),
        ('OUT', _('Check Out')),
        ('RE', _('Returned')),
        ('LO', _('Lost'))
    )

    user_profile = models.ForeignKey(UserProfile, null=True, on_delete=models.DO_NOTHING, verbose_name='用户')
    book = models.ForeignKey(Book, null=True, on_delete=models.DO_NOTHING, verbose_name='书名')
    book_status = models.CharField('书籍状态', choices=BOOK_STATUS, default='ON', null=False, max_length=10)
    time = models.DateTimeField('借阅时间', default=timezone.now)
    type = models.CharField(_('Type'), max_length=2, choices=TYPE, default='SC')
    return_date = models.DateField('归还日期', default=calc_return_date)
    returned_time = models.DateTimeField('归还时间', null=True, blank=True)
    allow_shift = models.BooleanField(_('Allow Shift'), default=True)

    class Meta:
        verbose_name = '借阅'
        verbose_name_plural = '借阅'

    def __repr__(self):
        return '<CheckOut {id: %s, book: %s, user: %s}>' % \
               (self.id, self.book.name if self.book else '#', self.user.username if self.user else '#')

    def __str__(self):
        return '%s -> %s' % (self.book.name, self.user_profile.user.username) if \
            self.user_profile and self.user_profile.user and self.book else '#->#'


class Comment(Base):
    checkout = models.ForeignKey(CheckOut, verbose_name='借出', on_delete=models.DO_NOTHING, null=True)
    score = models.FloatField(_('Score'), default=5.0)
    content = models.TextField(_('Content'), max_length=500)

    class Meta:
        verbose_name = _('评论')
        verbose_name_plural = _('评论')

    def __str__(self):
        return str(self.score)


class Note(Base):
    """笔记"""

    checkout = models.ForeignKey(CheckOut, verbose_name=_('CheckOut'), on_delete=models.DO_NOTHING, null=True)
    page = models.FloatField(_('Page'), default=1)
    content = models.TextField(_('Content'), max_length=500)

    class Meta:
        verbose_name = _('Note')
        verbose_name_plural = _('Note')

    def __repr__(self):
        return '<Note {id: %s, page: %s}>' % (self.id, self.page)

    def __str__(self):
        if self.checkout:
            return '%s:%s' % (self.checkout.book.name, self.page)
        else:
            return '1'


class Rent(Base):
    """租阅"""

    PAY_STATUS = (
        (-2, _('Failed')),
        (1, _('Paying')),
        (2, _('Success')),
    )
    checkout = models.ForeignKey(CheckOut, verbose_name=_('CheckOut'), on_delete=models.DO_NOTHING, null=True)
    days = models.IntegerField(_('Days'), default=1)
    amount = models.DecimalField(_('Amount'), max_digits=10, decimal_places=2, default=0.0)
    order_no = models.CharField(_('Order No'), max_length=50, blank=True)
    trade_no = models.CharField(_('Trade No'), max_length=50, blank=True)
    pay_status = models.IntegerField(_('Pay Status'), choices=PAY_STATUS, default=1)

    class Meta:
        verbose_name = _('Rent')
        verbose_name_plural = _('Rent')

    def __repr__(self):
        return '<Rent {id: %s, amount: %s}>' % (self.id, self.amount)

    def __str__(self):
        if self.checkout:
            return '%s:%s' % (self.checkout.book.name, self.amount)
        else:
            return '0.0'


class Shift(Base):
    """转借"""

    SHIFT_STATUS = (
        ('Req', _('Requested')),
        ('Arg', _('Agreed')),
        ('Com', _('Completed')),
        ('Abr', _('Abort')),
        ('Ref', _('Refused'))
    )
    checkout = models.ForeignKey(CheckOut, verbose_name=_('CheckOut'), on_delete=models.DO_NOTHING, null=True)
    request_user_profile = models.ForeignKey(UserProfile, verbose_name=_('Request User'),
                                             on_delete=models.DO_NOTHING, null=True)
    reason = models.TextField(_('Reason'), max_length=100)
    agreed = models.BooleanField(_('Agreed'), default=False)
    reply = models.TextField(_('Reply'), max_length=100, blank=True)
    shift_status = models.CharField(_('Pay Status'), choices=SHIFT_STATUS, default='Req', max_length=3)
    request_time = models.DateTimeField(_('Request Time'), default=timezone.now)
    reply_time = models.DateTimeField(_('Reply Time'), null=True, blank=True)
    complete_time = models.DateTimeField(_('Complete Time'), null=True, blank=True)

    class Meta:
        verbose_name = _('Shift')
        verbose_name_plural = _('Shift')

    def __repr__(self):
        return '<Shift {id: %s}>' % (self.id,)

    def __str__(self):
        if self.checkout and self.request_user_profile and self.request_user_profile.user:
            return '%s:%s' % (self.checkout.book.name, self.request_user_profile.user.username)
        else:
            return '----'


class Feedback(Base):
    """意见反馈"""

    user_profile = models.ForeignKey(UserProfile, verbose_name=_('User'), on_delete=models.DO_NOTHING, null=True)
    content = models.TextField(_('Content'), max_length=300, )
    wx_form_id = models.CharField(max_length=100, null=True, editable=False)
    reply = models.TextField(_('Reply'), max_length=200, blank=True)
    reply_time = models.DateTimeField(_('Reply Time'), null=True, blank=True)

    class Meta:
        verbose_name = _('Feedback')
        verbose_name_plural = _('Feedback')

    def __repr__(self):
        return '<Feedback {id: %s, content: %s}>' % (self.id, self.content)

    def __str__(self):
        return self.content if len(self.content) < 35 else self.content[:35] + '..'
