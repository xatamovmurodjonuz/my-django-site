from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import stripe

from .models import Business, Category, Tag, Like
from .forms import BusinessForm, CommentForm, RatingForm

stripe.api_key = settings.STRIPE_SECRET_KEY

def business_list(request):
    categories = Category.objects.all()
    tags = Tag.objects.all()
    queryset = Business.objects.all()

    cat_id = request.GET.get('category')
    tag_ids = request.GET.getlist('tags')
    query = request.GET.get('q')

    if cat_id:
        queryset = queryset.filter(category_id=cat_id)
    if tag_ids:
        queryset = queryset.filter(tags__in=tag_ids).distinct()
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query)
        )

    context = {
        'businesses': queryset,
        'categories': categories,
        'tags': tags,
        'selected_category': int(cat_id) if cat_id else None,
        'selected_tags': [int(i) for i in tag_ids] if tag_ids else [],
        'query': query,
    }
    return render(request, 'businesses/business_list.html', context)


@login_required
def business_create(request):
    if request.method == 'POST':
        form = BusinessForm(request.POST, request.FILES)
        if form.is_valid():
            business = form.save(commit=False)
            business.owner = request.user
            business.save()
            form.save_m2m()
            messages.success(request, "Biznes muvaffaqiyatli yaratildi.")
            return redirect('business_list')
        else:
            messages.error(request, "Iltimos, forma to‘g‘ri to‘ldiring.")
    else:
        form = BusinessForm()
    return render(request, 'businesses/business_create.html', {'form': form})


def business_detail(request, pk):
    business = get_object_or_404(Business, pk=pk)
    comments = business.comments.all().order_by('-created_at')
    average_rating = business.ratings.aggregate(avg=Avg('stars'))['avg'] or 0
    average_rating = round(average_rating, 1)

    form = CommentForm()
    rating_form = RatingForm()

    if request.method == 'POST':
        if 'comment_submit' in request.POST:
            if request.user.is_authenticated:
                form = CommentForm(request.POST)
                if form.is_valid():
                    comment = form.save(commit=False)
                    comment.business = business
                    comment.author = request.user
                    comment.save()
                    messages.success(request, "Kommentaringiz qo‘shildi.")
                    return redirect('business_detail', pk=pk)
                else:
                    messages.error(request, "Kommentaringizni tekshirib chiqing.")
            else:
                messages.error(request, "Kommentariya qo‘shish uchun tizimga kirishingiz kerak.")
                return redirect('login')
        elif 'rating_submit' in request.POST:
            if request.user.is_authenticated:
                rating_form = RatingForm(request.POST)
                if rating_form.is_valid():
                    stars = int(rating_form.cleaned_data['stars'])
                    rating, created = business.ratings.update_or_create(
                        user=request.user,
                        defaults={'stars': stars}
                    )
                    messages.success(request, "Reytingingiz qabul qilindi!")
                    return redirect('business_detail', pk=pk)
                else:
                    messages.error(request, "Reytingni to‘g‘ri tanlang.")
            else:
                messages.error(request, "Reyting qo‘yish uchun tizimga kirishingiz kerak.")
                return redirect('login')

    context = {
        'business': business,
        'comments': comments,
        'form': form,
        'rating_form': rating_form,
        'average_rating': average_rating,
        'total_likes': business.total_likes(),
        'total_dislikes': business.total_dislikes(),
    }
    return render(request, 'businesses/business_detail.html', context)


@login_required
def business_premium(request, pk):
    business = get_object_or_404(Business, pk=pk)
    if business.owner != request.user:
        messages.error(request, "Siz bu biznesga ega emassiz.")
        return redirect('business_detail', pk=pk)

    if request.method == 'POST':
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'Premium for {business.name}',
                        },
                        'unit_amount': 5000,  # 50.00 USD (cents)
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/businesses/') + '?success=true',
                cancel_url=request.build_absolute_uri('/businesses/') + '?cancelled=true',
            )
            return redirect(checkout_session.url)
        except Exception as e:
            messages.error(request, f"To‘lovda xatolik yuz berdi: {e}")

    context = {
        'business': business,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'businesses/business_premium.html', context)

@require_POST
@login_required
def business_like_toggle(request, pk):
    business = get_object_or_404(Business, pk=pk)
    user = request.user
    value = request.POST.get('value')

    if value not in ['1', '-1']:
        return JsonResponse({'error': 'Noto‘g‘ri qiymat'}, status=400)

    value = int(value)

    like_obj, created = Like.objects.get_or_create(
        user=user,
        business=business,
        defaults={'value': value}
    )

    if not created:
        if like_obj.value == value:
            like_obj.delete()
            status = 'removed'
        else:
            like_obj.value = value
            like_obj.save()
            status = 'updated'
    else:
        status = 'created'

    data = {
        'status': status,
        'total_likes': business.total_likes(),
        'total_dislikes': business.total_dislikes(),
    }
    return JsonResponse(data)
