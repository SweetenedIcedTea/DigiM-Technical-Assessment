from django.contrib import admin
from django.utils.html import format_html
from .models import Folder, Image
from typing import List, Optional, Tuple


class ImageInline(admin.TabularInline):
    """
    Inline admin interface for Images within Folder admin.
    
    Displays images as a tabular inline within the folder admin page,
    allowing for efficient management of images in a folder.
    """
    model = Image
    readonly_fields = ['preview_image', 'width', 'height', 'file_size', 'is_color']
    fields = ['preview_image', 'name', 'image_file', 'width', 'height', 'file_size', 'is_color']
    extra = 0  # Don't show empty rows for adding new images
    
    def preview_image(self, obj: Optional[Image]) -> str:
        """
        Generate an HTML thumbnail preview for the image.
        
        Args:
            obj: The Image instance
            
        Returns:
            HTML string containing an image tag with thumbnail
        """
        if obj and obj.image_file:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 100px;">',
                obj.image_file.url
            )
        return "-"
    
    preview_image.short_description = "Preview"


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    """
    Admin interface for Folder model.
    
    Provides an intuitive interface for managing folders, with list views 
    showing key information and filtering options.
    """
    list_display = ['name', 'slug', 'created_at', 'image_count']
    list_filter = ['created_at']
    search_fields = ['name', 'slug']
    readonly_fields = ['image_count', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ImageInline]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    """
    Admin interface for Image model.
    
    Provides a comprehensive interface for managing images, with list views
    showing key information, image preview, and filtering options.
    """
    list_display = ['preview_thumbnail', 'name', 'folder', 'upload_date', 'dimensions', 'formatted_file_size_admin']
    list_filter = ['folder', 'upload_date', 'is_color']
    search_fields = ['name', 'folder__name']
    readonly_fields = ['preview_image', 'width', 'height', 'file_size', 'is_color', 'formatted_file_size_admin']
    fields = ['folder', 'name', 'preview_image', 'image_file', 'width', 'height', 'file_size', 'is_color']
    
    def preview_thumbnail(self, obj: Image) -> str:
        """
        Generate an HTML thumbnail preview for list view.
        
        Args:
            obj: The Image instance
            
        Returns:
            HTML string containing an image tag with thumbnail
        """
        if obj.image_file:
            return format_html(
                '<img src="{}" style="max-height: 40px; max-width: 80px;">',
                obj.image_file.url
            )
        return "-"
    
    preview_thumbnail.short_description = ""
    
    def preview_image(self, obj: Image) -> str:
        """
        Generate a larger HTML preview for detail view.
        
        Args:
            obj: The Image instance
            
        Returns:
            HTML string containing an image tag with preview
        """
        if obj.image_file:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 400px;">',
                obj.image_file.url
            )
        return "-"
    
    preview_image.short_description = "Preview"
    
    def dimensions(self, obj: Image) -> str:
        """
        Format image dimensions for display.
        
        Args:
            obj: The Image instance
            
        Returns:
            String with formatted dimensions
        """
        return f"{obj.width} × {obj.height}"
    
    dimensions.short_description = "Dimensions"
    
    def formatted_file_size_admin(self, obj: Image) -> str:
        """
        Format file size for admin display.
        
        Args:
            obj: The Image instance
            
        Returns:
            Formatted file size string
        """
        return obj.formatted_file_size
    
    formatted_file_size_admin.short_description = "File Size"