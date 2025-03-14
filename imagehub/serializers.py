from rest_framework import serializers
from .models import Folder, Image
from typing import Dict, Any

class ImageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Image model.
    
    Handles conversion between Image model instances and their JSON representations.
    Provides validation and deserialization for image creation.
    """
    formatted_file_size = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = Image
        fields = [
            'id', 'folder', 'name', 'slug', 'image_file', 'upload_date',
            'width', 'height', 'file_size', 'formatted_file_size',
            'is_color', 'url'
        ]
        read_only_fields = [
            'id', 'folder', 'name', 'slug', 'width', 'height', 
            'file_size', 'is_color', 'upload_date'
        ]
    
    def get_formatted_file_size(self, obj: Image) -> str:
        """
        Get human-readable file size.
        
        Args:
            obj: The Image instance being serialized
            
        Returns:
            Formatted file size string
        """
        return obj.formatted_file_size
    
    def get_url(self, obj: Image) -> str:
        """
        Get the full URL to the image file.
        
        Args:
            obj: The Image instance being serialized
            
        Returns:
            URL string for the image file
        """
        request = self.context.get('request')
        if request is None:
            return obj.image_file.url
        
        return request.build_absolute_uri(obj.image_file.url)


class FolderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Folder model.
    
    Handles conversion between Folder model instances and their JSON representations.
    Includes nested ImageSerializer data for related images.
    """
    images = ImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Folder
        fields = ['id', 'name', 'slug', 'created_at', 'image_count', 'images']
        read_only_fields = ['id', 'slug', 'created_at', 'image_count']
    
    def create(self, validated_data: Dict[str, Any]) -> Folder:
        """
        Create a new Folder instance.
        
        Args:
            validated_data: The validated data from the request
            
        Returns:
            The newly created Folder instance
        """
        return Folder.objects.create(**validated_data)