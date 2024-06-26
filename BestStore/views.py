from django.shortcuts import render, get_object_or_404, redirect # type: ignore
from store.models import Product, ReviewRating
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.http import HttpResponse # type: ignore
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator # type: ignore
from django.db.models import Q # type: ignore
from store.forms import ReviewForm
from django.contrib import messages # type: ignore
from store.models import ReviewRating
# Create your views here.

# Home url
def home(request): 
     products = Product.objects.all().filter(is_available=True)
     #review_rating = ReviewRating.objects.filter(product_id=products, status=True)
     context = {
          'products': products,
          
     }
     return render(request, 'BestStore/home.html', context)

def store(request, category_slug=None): 
     categories = None 
     products = None 
     if category_slug != None: 
          categories = get_object_or_404(Category, slug=category_slug)
          products = Product.objects.filter(category=categories, is_available=True)
          paginator = Paginator(products, 3) # 6 is the number of products on a single page 
          page = request.GET.get('page') # getting the page number from the browser
          page_products = paginator.get_page(page)   
          product_count = products.count()

     else: 
        products = Product.objects.all().filter(is_available=True).order_by('id')
        # Handling paginator for the product page
        paginator = Paginator(products, 3) # 6 is the number of products on a single page 
        page = request.GET.get('page') # getting the page number from the browser
        page_products = paginator.get_page(page)   
        product_count = products.count()
     
    

     context = {
          'categories': Category.objects.all(),
          'products': page_products,
          'product_count': product_count,
          
     }
     return render(request, 'BestStore/store/store.html', context)
def product_detail(request, category_slug, product_slug): 
     try: 
          product = Product.objects.get(category__slug=category_slug, slug=product_slug)
          in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=product).exists()
          
     except Exception as e: 
          raise e 
     
     review_rating = ReviewRating.objects.filter(product_id=product.id, status=True)
     context = {
          'single_product': product,
          'in_cart': in_cart,
          'reviews': review_rating
     }

     return render(request, 'BestStore/store/product_detail.html', context)

def search(request): 
     keyword = request.GET['keyword']
     if keyword: 
               products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword) | Q(slug__icontains=keyword))
               
               product_count = products.count()
     else: 
          return redirect('store')
     
     context = {
          'products': products,
          'product_count': product_count
     }

     return render(request, 'BestStore/store/store.html', context)


def submit_review(request, product_id): 
     url = request.META.get('HTTP_REFERER')
     if request.method == "POST": 
          try: 
               reviews = ReviewRating.objects.get(user__id=request.user.id, product__id = product_id)
               form = ReviewForm(request.POST, instance=reviews)
               form.save()
               messages.success(request, 'Thank you! Your review has been updated')
               return redirect(url)
          except ReviewRating.DoesNotExist: 
               form = ReviewForm(request.POST)
               if form.is_valid(): 
                    data = ReviewRating()
                    data.subject = form.cleaned_data['subject']
                    data.rating = form.cleaned_data['rating']
                    data.review = form.cleaned_data['review']
                    data.ip = request.META.get('REMOTE_ADDR')
                    data.product_id = product_id
                    data.user_id = request.user.id
                    data.save()
                    messages.success(request, 'thank you!, your review has been submitted')
                    return redirect(url)
