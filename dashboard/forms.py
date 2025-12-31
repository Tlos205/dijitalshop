from django import forms
from products.models import Product, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'product_type', 'price', 'discount_price',
            'short_description', 'description', 'detailed_description', 'tags',
            'preview_image', 'file', 'file_size', 'file_format', 'version',
            'compatibility', 'is_active', 'is_featured'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'detailed_description': forms.Textarea(attrs={'rows': 6}),
            'tags': forms.TextInput(attrs={
                'placeholder': 'шаблон, сайт, бизнес, дизайн'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поле файла необязательным при редактировании
        self.fields['file'].required = False

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'slug': forms.TextInput(attrs={
                'placeholder': 'Будет сгенерирован автоматически'
            })
        }