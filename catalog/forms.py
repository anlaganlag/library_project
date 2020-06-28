from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
#dj的翻译函数ugettext_lazy
import datetime  # 用来判断日期区间

from django import forms
from django.forms import ModelForm

from .models import BookInstance


# class RenewBookForm(forms.Form):
#     """一个表单,方便图书管理员续借"""
#     renewal_date = forms.DateField(
#             help_text="请输入一个4周以内的时间,默认时间3周..")

#     def clean_renewal_date(self):
#         #这里用默认表单验证工具,cleanend_data..
#         #使用了默认的验证器,完成了对数据的清理,清楚可能不安全的输入
#         #将数据转换成正确的标准类型即py的datetime.datetime对象
#         data = self.cleaned_data['renewal_date']

#         #更新日期不能在本日之前
#         if data < datetime.date.today():
#             raise ValidationError(_('无效日期- renewal in past'))
#         #更行日期是否超过了4周的借个
#         if data > datetime.date.today() + datetime.timedelta(weeks=4):
#             raise ValidationError(
#                 _('Invalid date - renewal more than 4 weeks ahead'))

#         #切记要返回更新后的日期..
#         return data


#这里使用的是ModelForm
class RenewBookModelForm(ModelForm):
    def clean_due_back(self):
       data = self.cleaned_data['due_back']
       
       #Check date is not in past.
       if data < datetime.date.today():
           raise ValidationError(_('Invalid date - renewal in past'))

       #Check date is in range librarian allowed to change (+4 weeks)
       if data > datetime.date.today() + datetime.timedelta(weeks=4):
           raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

       # Remember to always return the cleaned data.
       return data

    class Meta:
        model = BookInstance
        fields = ['due_back',]
        labels = { 'due_back': _('Renewal date'), }
        help_texts = { 'due_back': _('Enter a date between now and 4 weeks (default 3).'), } 