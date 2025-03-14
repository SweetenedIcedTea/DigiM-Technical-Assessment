from django.db import models
from django.utils.text import slugify
import os
from typing import Any, Optional
from PIL import Image as PILImage
from django.core.validators import FileExtensionValidator, MaxValueValidator

def generate_unique_slug(
    model_class: models.Model, 
    name: str, 
    folder_id: Optional[int] = None
) -> str:
    """
    Generate a unique slug based on a name.
    
    Args:
        model_class: The model class to check for slug existence
        name: The name to generate a slug from
        folder_id: Optional folder ID for Image model to ensure uniqueness within folder
        
    Returns:
        A unique slug string
    """
    base_slug = slugify(name)
    slug = orig = base_slug
    count = 1
    
    # Build filter arguments
    filter_kwargs = {'slug': slug}
    if folder_id is not None:
        filter_kwargs['folder_id'] = folder_id
        
    # Check for uniqueness and increment counter if needed
    while model_class.objects.filter(**filter_kwargs).exists():
        slug = f"{orig}-{count}"
        filter_kwargs['slug'] = slug
        count += 1
        
    return slug


def upload_to_path(instance: 'Image', filename: str) -> str:
    """
    Generate upload path for images based on folder ID.
    
    Args:
        instance: The Image instance being saved
        filename: The original filename
        
    Returns:
        A path string where the file will be stored
    """
    return f"uploads/{instance.folder.id}/{filename}"


def format_file_size(bytes: int) -> str:
    """
    Format file size from bytes to readable format.
    
    Args:
        bytes: Size in bytes
        
    Returns:
        Formatted file size string with appropriate unit
    """
    if bytes < 1024:
        return f"{bytes} bytes"
    elif bytes < 1024 * 1024:
        return f"{bytes/1024:.1f} KB"
    else:
        return f"{bytes/(1024*1024):.1f} MB"


class Folder(models.Model):
    """
    Represents a folder that can contain multiple images.
    
    A folder has a unique name and slug, and keeps track of how many images it contains.
    """
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image_count = models.PositiveIntegerField(default=0, editable=False)

    @property
    def images(self) -> models.QuerySet:
        """
        Get all images in this folder.
        
        Returns:
            QuerySet of all related Image objects
        """
        return self.image_set.all()

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Override save method to generate unique slug if not provided.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        if not self.slug:
            self.slug = generate_unique_slug(Folder, self.name)
        super().save(*args, **kwargs)

    def update_image_count(self) -> None:
        """
        Update the image count for this folder based on actual related images.
        """
        self.image_count = self.image_set.count()
        self.save(update_fields=['image_count'])

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        ordering = ['name']


class Image(models.Model):
    """
    Represents an image file associated with a folder.
    
    Stores metadata about the image including dimensions, file size,
    and whether it's a color or grayscale image.
    """
    folder = models.ForeignKey(
        Folder, 
        on_delete=models.CASCADE,
        related_name='image_set'
    )
    name = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255)
    image_file = models.ImageField(
        upload_to=upload_to_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif']),
        ]
    )
    upload_date = models.DateTimeField(auto_now_add=True)
    width = models.PositiveIntegerField(editable=False)
    height = models.PositiveIntegerField(editable=False)
    file_size = models.PositiveIntegerField(editable=False)
    is_color = models.BooleanField(editable=False)

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Override save method to:
        1. Set name based on filename
        2. Generate unique slug within folder
        3. Extract and save image metadata
        4. Update parent folder's image count
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
            
        Raises:
            ValueError: If the image file is invalid
        """
        
        # Set name from filename
        if self.image_file:
            filename = os.path.basename(self.image_file.name)
            self.name = os.path.splitext(filename)[0]

        # Generate slug from name, unique within the folder
        if self.name and self.folder:
            self.slug = generate_unique_slug(Image, self.name, self.folder.id)

        # Process image metadata for new images
        if not self.pk:
            try:
                self.image_file.seek(0)
                with PILImage.open(self.image_file) as img:
                    self.width, self.height = img.size
                    self.is_color = img.mode != 'L'
                self.file_size = self.image_file.size
            except Exception as e:
                raise ValueError(f"Invalid image file: {str(e)}")

        super().save(*args, **kwargs)
        
        # Update the parent folder's image count
        self.folder.update_image_count()
    
    @property
    def formatted_file_size(self) -> str:
        """
        Return a human-readable file size.
        
        Returns:
            String representation of file size with appropriate unit
        """
        return format_file_size(self.file_size)
    
    def __str__(self) -> str:
        return self.name
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['folder', 'slug'],
                name='unique_folder_slug'
            )
        ]
        ordering = ['-upload_date']