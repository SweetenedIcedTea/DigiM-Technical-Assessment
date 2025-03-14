from django.urls import path
from .views import (
    FolderListCreate,
    FolderDetail,
    ImageListCreate,
    ImageDetail,
)

app_name = 'imagehub'

# Group URL patterns by API vs Web interfaces
api_urlpatterns = [
    # Folder endpoints
    path(
        'api/folders/', 
        FolderListCreate.as_view(), 
        name='folder-list'
    ),
    path(
        'api/folders/<str:folder_identifier>/', 
        FolderDetail.as_view(), 
        name='folder-detail'
    ),
    
    # Image endpoints
    path(
        'api/folders/<str:folder_identifier>/images/', 
        ImageListCreate.as_view(), 
        name='image-list'
    ),
    path(
        'api/folders/<str:folder_identifier>/images/<str:image_identifier>/', 
        ImageDetail.as_view(),  # Note: Using the new API view
        name='image-detail-api'
    ),
]

# Combine all URL patterns
urlpatterns = api_urlpatterns