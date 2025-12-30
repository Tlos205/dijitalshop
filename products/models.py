from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator
from django.utils.text import slugify
import transliterate 


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Изображение")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Транслитерируем русский текст в латиницу
            try:
                import transliterate
                transliterated = transliterate.translit(self.name, 'ru', reversed=True)
                self.slug = slugify(transliterated)
            except:
                # Если transliterate не установлен, используем простой slugify
                self.slug = slugify(self.name)
        super().save(*args, **kwargs)



class Product(models.Model):
    TYPE_CHOICES = [
        ('template', 'Шаблон сайта'),
        ('graphics', 'Графика'),
        ('ebook', 'Электронная книга'),
        ('software', 'Программное обеспечение'),
        ('course', 'Курс'),
        ('music', 'Музыка'),
        ('photo', 'Фотографии'),
        ('other', 'Другое'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    name = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL")
    short_description = models.CharField(max_length=300, verbose_name="Краткое описание")
    description = models.TextField(verbose_name="Описание")
    detailed_description = models.TextField(blank=True, verbose_name="Подробное описание")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Цена",
        validators=[MinValueValidator(0)]
    )
    discount_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Цена со скидкой",
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    file = models.FileField(upload_to='products/files/', verbose_name="Файл товара")
    preview_image = models.ImageField(upload_to='products/previews/', verbose_name="Превью")
    additional_images = models.ImageField(upload_to='products/additional/', blank=True, null=True, verbose_name="Дополнительные изображения")
    product_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other', verbose_name="Тип товара")
    tags = models.CharField(max_length=200, blank=True, verbose_name="Теги")
    file_size = models.CharField(max_length=50, blank=True, verbose_name="Размер файла")
    file_format = models.CharField(max_length=20, blank=True, verbose_name="Формат файла")
    version = models.CharField(max_length=20, blank=True, verbose_name="Версия")
    compatibility = models.CharField(max_length=200, blank=True, verbose_name="Совместимость")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_featured = models.BooleanField(default=False, verbose_name="Рекомендуемый")
    sales_count = models.IntegerField(default=0, verbose_name="Количество продаж")
    view_count = models.IntegerField(default=0, verbose_name="Количество просмотров")
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})
    
    @property
    def get_slug_or_id(self):
        """Возвращает slug или ID если slug отсутствует"""
        if self.slug:
            return self.slug
        return str(self.id)
    
    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price
    
    @property
    def has_discount(self):
        return self.discount_price is not None
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class ProductFeature(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='features')
    name = models.CharField(max_length=100, verbose_name="Название характеристики")
    value = models.CharField(max_length=200, verbose_name="Значение")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    
    class Meta:
        verbose_name = "Характеристика товара"
        verbose_name_plural = "Характеристики товаров"
        ordering = ['order']
    
    def __str__(self):
        return f"{self.name}: {self.value}"