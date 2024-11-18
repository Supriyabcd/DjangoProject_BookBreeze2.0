from django.contrib import admin
from .models import Book, Price, Genre, UserProfile, Rating, Review, Shelf, BookList

class PriceAdmin(admin.ModelAdmin):
    list_display = ('website', 'price')

class PriceInline(admin.TabularInline):
    model = Price
    extra = 1

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_date', 'get_price', 'get_website')  # Updated
    filter_horizontal = ('genres',)
    search_fields = ('title', 'author', 'genres__name')  # Updated to search in the Genre model
    inlines = [PriceInline]

    # Method to display the price in list_display
    def get_price(self, obj):
        # Get the first related Price object for this book
        price = obj.prices.first()  # Adapt this logic based on your requirement
        return price.price if price else 'N/A'  # If no price, return 'N/A'

    # Method to display the website in list_display
    def get_website(self, obj):
        # Get the first related Price object for this book
        price = obj.prices.first()
        return price.website if price else 'N/A'  # If no website, return 'N/A'

    # Optional: Customize the column titles
    get_price.short_description = 'Price'
    get_website.short_description = 'Website'

class UserAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'gender', 'profession', 'languages')
    filter_horizontal = ('genres', 'want_to_read', 'currently_reading', 'read')

class RatingAdmin(admin.ModelAdmin):
    display = ('book', 'user', 'rating')

class ReviewAdmin(admin.ModelAdmin):
    display = ('book', 'user', 'review')

class ShelfAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_profile', 'category')
    list_filter = ('category',)
    # search_fields = ('name', 'category__name')

class BookListAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'book_item', 'list_type', 'added_at', 'progress')
    search_fields = ('user_profile_userusername', 'book_item_title')

admin.site.register(Book, BookAdmin)
admin.site.register(Genre)
admin.site.register(Price, PriceAdmin)  # Optionally use PriceAdmin for better display of Price
admin.site.register(UserProfile, UserAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Shelf, ShelfAdmin)
admin.site.register(BookList, BookListAdmin)


