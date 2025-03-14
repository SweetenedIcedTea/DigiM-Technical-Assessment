from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from typing import Any, Dict, Optional, Type, TypeVar

from .models import Folder, Image
from .serializers import FolderSerializer, ImageSerializer

T = TypeVar('T', Folder, Image)  # Type variable for get_object_by_identifier


def get_object_by_identifier(
    model_class: Type[T], 
    identifier: str, 
    parent_filter: Optional[Dict[str, Any]] = None
) -> T:
    """
    Retrieve a model object by identifier which could be an ID or slug.
    
    Args:
        model_class: The model class to query
        identifier: Either a numeric ID or a string slug
        parent_filter: Optional additional filter parameters (e.g., folder=folder)
        
    Returns:
        The retrieved object
        
    Raises:
        Http404: If the object doesn't exist
    """
    filters = {}
    if parent_filter:
        filters.update(parent_filter)
        
    if identifier.isdigit():
        filters['id'] = int(identifier)
    else:
        filters['slug'] = identifier
        
    return get_object_or_404(model_class, **filters)


class FolderListCreate(generics.ListCreateAPIView):
    """
    API endpoint for listing all folders and creating new ones.
    
    GET: List all folders
    POST: Create a new folder
    """
    serializer_class = FolderSerializer
    permission_classes = [permissions.AllowAny]  # TODO: Implement proper authentication
    
    def get_queryset(self):
        """Return all folders with prefetched images."""
        return Folder.objects.prefetch_related('image_set').all()


class FolderDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving a single folder's details.
    
    GET: Retrieve folder details by ID or slug
    """
    serializer_class = FolderSerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Return all folders with prefetched images."""
        return Folder.objects.all()
    
    def get_object(self) -> Folder:
        """
        Get folder by ID or slug.
        
        Returns:
            The requested Folder object
        """
        identifier = self.kwargs['folder_identifier']
        return get_object_by_identifier(Folder, identifier)


class ImageListCreate(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating images within a folder.
    
    GET: List all images in a folder
    POST: Create a new image in a folder
    """
    serializer_class = ImageSerializer

    def get_queryset(self):
        """
        Return all images for the specified folder.
        
        Returns:
            QuerySet of all images in the folder
        """
        folder = self.get_folder()
        return folder.image_set.all()

    def get_folder(self) -> Folder:
        """
        Get the folder specified in the URL.
        
        Returns:
            The Folder object
        """
        identifier = self.kwargs['folder_identifier']
        return get_object_by_identifier(Folder, identifier)

    def perform_create(self, serializer) -> None:
        """
        Save the image with the correct folder.
        
        Args:
            serializer: The ImageSerializer instance
        """
        serializer.save(folder=self.get_folder())

class ImageDetail(DetailView):
    """
    Web interface for viewing image details.
    
    Template-based view that renders the image_detail.html template.
    """
    model = Image
    template_name = 'imagehub/image_detail.html'
    context_object_name = 'image'

    def get_object(self) -> Image:
        """
        Get image by ID or slug within a specific folder.
        
        Returns:
            The requested Image object
        """
        folder_identifier = self.kwargs['folder_identifier']
        image_identifier = self.kwargs['image_identifier']
        
        folder = self.get_folder(folder_identifier)
        return get_object_by_identifier(
            Image, 
            image_identifier, 
            {'folder': folder}
        )

    def get_folder(self, identifier: str) -> Folder:
        """
        Get folder by ID or slug.
        
        Args:
            identifier: Either a numeric ID or a string slug
            
        Returns:
            The Folder object
        """
        return get_object_by_identifier(Folder, identifier)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """
        Enhance context with formatted file size and dates.
        
        Returns:
            Context dictionary with additional formatting
        """
        context = super().get_context_data(**kwargs)
        image = context['image']
        
        # Add formatted file size
        context['file_size_formatted'] = image.formatted_file_size
        
        # Format dates
        upload_date = image.upload_date
        context['formatted_date'] = upload_date.strftime('%B %d, %Y')
        context['formatted_time'] = upload_date.strftime('%I:%M %p')
        
        return context