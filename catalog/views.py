from django.shortcuts import render,get_object_or_404

from django.contrib.auth.mixins import  LoginRequiredMixin ,PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required

from django.http import HttpResponseRedirect
from django.urls import reverse,reverse_lazy

from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .forms import RenewBookForm
from .models import Book,Author,BookInstance,Genre

import datetime


def index(request):
    """展示主页的函数"""
    #展示书及书的实例以及作者数量!
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_authors = Author.objects.count()  # The 'all()' is implied by default.
    #a 即Available即可以借的书的数目
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # 使用了session这个类似字典的功能..每次访问都+1
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1

    return render(
        request,
        'index.html',
        context={'num_books': num_books, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available, 'num_authors': num_authors,
                 'num_visits': num_visits},
    )


class BookListView(generic.ListView):
    model = Book
    context_object_name = 'my_book_list'  
     # 设定书的列表的模板变量,在模板中使用
     #或者可以理解为将上下文变量传递给模板..
    queryset = Book.objects.filter(title__icontains='war')[:5] 
    #设定查询范围..比如.. 
    template_name = 'books/my_arbitrary_template_name_list.html'  
    #指明模板的位置及名字.. 
    paginate_by = 10

    def get_queryset(self):
        #重写类的方法,可以修改queryset的结果..比如在属性直接设定更灵活
        return Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        # 将更多的上下文context传个模板,则在模板中可以使用这些变量
        context = super(BookListView, self).get_context_data(**kwargs)
        #首先是集成基本的上下文context..
        context['some_data'] = 'This is just some data'
        #创建一些变量加入上下文context,kv對
        return context


class BookDetailView(generic.DetailView):
    """CBV用来展示特定的书,即书的具体页面"""
    model = Book



class AuthorListView(generic.ListView):
    """CBV用来展示作者的列表"""
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):

    """CBV用来展示特定的作者,即作者的具体信息页面"""
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """ CBV用来展示当前读者的所借书籍 """
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        #将查询queryset限定为当前用户的BookInstance对象..
        #重新实现了get_queryset()
        #这里的o代表on loan出借中..
        #按照归还的顺序排序的due_back..显示最快要归还项目..
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_inst=get_object_or_404(BookInstance, pk = pk)

    if request.method == 'POST':
        #创建了表单实例并填写了post信息相当于绑定数据和表单
        form = RenewBookForm(request.POST)

        if form.is_valid():
            #用form.cleaned_data处理数据,并保存到归还日期..
            book_inst.due_back = form.cleaned_data['renewal_date']
            #保存到db中
            book_inst.save()
            #重定向到一个新的地址..
            return HttpResponseRedirect(reverse('all-borrowed') )
    #如果是一个get的方法..
    else:
            #自动他提供参考日期3周之后..
            proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
            #表单的初始值是建议值..
            form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})
            return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})

class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'05/01/2018',}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')