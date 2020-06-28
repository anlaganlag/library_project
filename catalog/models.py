from django.db import models
from django.urls import reverse 

import uuid  # Required for unique book instances
from datetime import date

from django.contrib.auth.models import User  # Required to assign User as a borrower

class Genre(models.Model):
    """Model representing a book genre (e.g. Science Fiction, Non Fiction)."""
    name = models.CharField(
        max_length=200,
        help_text="Enter a book genre (e.g. Science Fiction, French Poetry etc.)"
        )

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name


class Language(models.Model):
    """Model representing a Language (e.g. English, French, Japanese, etc.)"""
    name = models.CharField(max_length=200,
                            help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)")

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name


class Book(models.Model):
    """该模型是一本书的抽象概念,不是一本有唯一条码的实体书"""
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    #外键表明一本书只能有一个作者,但是一个作者可以对应多本书.
    summary = models.TextField(max_length=1000, help_text="请输入对本书的描述!")
    isbn = models.CharField('ISBN', max_length=13,
                            help_text='13 字符 <a href="https://www.isbn-international.org/content/what-isbn'
                                      '">ISBN 条码</a>')
    genre = models.ManyToManyField(Genre, help_text="书籍分类")
    #多对多即一本书可以对应多个分类,一个分类可以有多本书
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    def display_genre(self):
        """字符串表示分类,可以在admin中展示分类"""
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Genre'

    def get_absolute_url(self):
        """返回特定书的实例的url"""
        return reverse('book-detail', args=[str(self.id)])

    def __str__(self):
        return self.title




class BookInstance(models.Model):
    """代表一本实体书,可以被借出或者被阅读!,相当于抽象书的实例,有唯一标识imprint"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="每本实体书都有唯一的标识,保证不会和其他实例混淆")
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='d',
        help_text='Book availability')

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        return f'{self.id} {self.book.title}'


class Author(models.Model):
    """该模型代码代表一名作家"""
    first_name = models.CharField(verbose_name="姓",max_length=100)
    last_name = models.CharField(verbose_name="名",max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """返回特定作家实例的url地址"""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.first_name}{self.last_name}'