from urllib import request
from django.shortcuts import render
from django.views import generic
from django.shortcuts import get_object_or_404
from .models import Book, Author, BookInstance, Genre
from .constant import LOAN_STATUS, NUM_BOOK_VIEW
# Create your views here.
from catalog.models import Book, Author, Genre, BookInstance

def index(request):
    """View function for home page of site."""
    
    #generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    
    #Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    
    #The 'all()' is implied by default, so we can use it directly
    num_authors = Author.objects.count() 
    
    #Number of visits to this view, as counted in the session variable
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1
    
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,  
    }
    
    #render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = NUM_BOOK_VIEW
    context_object_name = "book_list"
    template_name = "catalog/book_list.html"
    queryset = Book.objects.all().order_by("title")


class BookDetailView(generic.DetailView):
    """Generic class-based view for a book detail page."""

    model = Book

    def get_context_data(self, **kwargs):
        """Add additional context data to the view."""
        context = super(BookDetailView, self).get_context_data(**kwargs)
        context["LOAN_STATUS"] = LOAN_STATUS
        context["book_instances"] = self.object.bookinstance_set.all()
        return context

    def book_detali_view(self, primary_key):
        """View function for displaying a book detail page."""
        book = get_object_or_404(Book, pk=primary_key)

        return render(request, "catalog/book_detail.html", context={"book": book})
    
    