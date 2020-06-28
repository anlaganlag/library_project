from django.shortcuts import render
from django.views import generic
from .models import Book,Author,BookInstance,Genre


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