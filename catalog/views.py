import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Book, Author, BookInstance, Genre
from .constant import (
    LOAN_STATUS,
    NUM_BOOK_VIEW,
    NUM_VISITS,
    NUM_OF_WEEKS_DEFAULT,
    INITIAL_DATE_OF_DEATH,
)
from .form import RenewBookForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from catalog.models import Author

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


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
    

@login_required
@permission_required("catalog.can_mark_returned", raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    
    if request.method == "POST":
        form = RenewBookForm(request.POST)
        if form.is_valid():
            book_instance.due_back = form.cleaned_data["renewal_date"]
            book_instance.save()
            return HttpResponseRedirect(reverse("all-borrowed"))
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(
            weeks=NUM_OF_WEEKS_DEFAULT
        )
        form = RenewBookForm(initial={"renewal_date": proposed_renewal_date})

    context = {"form": form, "book_instance": book_instance}

    return render(request, "catalog/book_renew_librarian.html", context)

@login_required
@permission_required("catalog.can_mark_returned", raise_exception=True)
def borrow_book(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if book_instance.status != LOAN_STATUS.AVAILABLE.value:
        return redirect("book-detail", pk=book_instance.book.pk)

    book_instance.status = LOAN_STATUS.ON_LOAN.value
    book_instance.borrower = request.user
    book_instance.due_back = datetime.date.today() + datetime.timedelta(
        weeks=NUM_OF_WEEKS_DEFAULT
    )
    book_instance.save()

    return redirect("book-detail", pk=book_instance.book.pk)


class AuthorListView(generic.ListView):
    """Generic class-based view for a list of authors."""
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    """Generic class-based view for an author detail page."""
    model = Author


class AuthorCreate(CreateView):
    model = Author
    fields = ["first_name", "last_name", "date_of_birth", "date_of_death"]


class AuthorUpdate(UpdateView):
    model = Author
    fields = ["first_name", "last_name", "date_of_birth", "date_of_death"]


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy("authors")
    
    