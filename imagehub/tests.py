from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from .models import Folder, Image
import tempfile
import os
from PIL import Image as PILImage


class FolderModelTest(TestCase):
    def test_folder_creation(self):
        """Test that folders are created with correct slugs and counts."""
        folder = Folder.objects.create(name="Test Folder")
        self.assertEqual(folder.slug, "test-folder")
        self.assertEqual(folder.image_count, 0)
        
    def test_folder_unique_slug(self):
        """Test that names generating similar base slugs get unique slugs."""
        # Create folders with different names but similar resulting slugs
        folder1 = Folder.objects.create(name="Test Folder")
        folder2 = Folder.objects.create(name="Test-Folder")  # This would slug to 'test-folder' too
        
        # Verify the slugs are different
        self.assertEqual(folder1.slug, "test-folder")
        self.assertEqual(folder2.slug, "test-folder-1")


class ImageModelTest(TestCase):
    def setUp(self):
        self.folder = Folder.objects.create(name="Test Folder")
        
        # Create a test image file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as img_file:
            self.temp_image_path = img_file.name
            # Create a simple test image
            image = PILImage.new('RGB', (100, 100), color='red')
            image.save(self.temp_image_path)
    
    def tearDown(self):
        # Clean up the temporary file
        if os.path.exists(self.temp_image_path):
            os.unlink(self.temp_image_path)
    
    def test_image_creation(self):
        """Test that image metadata is extracted correctly."""
        with open(self.temp_image_path, 'rb') as img_file:
            image = Image(folder=self.folder)
            image.image_file.save('test_image.png', SimpleUploadedFile('test_image.png', img_file.read()))
        
        # Verify image attributes
        self.assertEqual(image.width, 100)
        self.assertEqual(image.height, 100)
        self.assertTrue(image.is_color)
        self.assertTrue(image.file_size > 0)
        
        # Verify folder image count update
        self.folder.refresh_from_db()
        self.assertEqual(self.folder.image_count, 1)


class APITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.folder = Folder.objects.create(name="Test Folder")
        
        # Create a test image file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as img_file:
            self.temp_image_path = img_file.name
            # Create a simple test image
            image = PILImage.new('RGB', (100, 100), color='red')
            image.save(self.temp_image_path)
    
    def tearDown(self):
        # Clean up the temporary file
        if os.path.exists(self.temp_image_path):
            os.unlink(self.temp_image_path)
    
    def test_folder_list(self):
        """Test that folder list API returns expected data."""
        # Add namespace to URL name
        url = reverse('imagehub:folder-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Folder')
    
    def test_folder_detail(self):
        """Test that folder detail API returns expected data."""
        # Add namespace to URL name
        url = reverse('imagehub:folder-detail', kwargs={'folder_identifier': self.folder.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Test Folder')
    
    def test_create_folder(self):
        """Test creating a folder via API."""
        # Add namespace to URL name
        url = reverse('imagehub:folder-list')
        response = self.client.post(url, {'name': 'New Folder'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Folder.objects.count(), 2)
        
    def test_image_upload(self):
        """Test uploading an image to a folder."""
        # Add namespace to URL name
        url = reverse('imagehub:image-list', kwargs={'folder_identifier': self.folder.slug})
        
        with open(self.temp_image_path, 'rb') as img_file:
            response = self.client.post(url, {
                'image_file': img_file
            }, format='multipart')
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Image.objects.count(), 1)
        
        # Verify folder image count updated
        self.folder.refresh_from_db()
        self.assertEqual(self.folder.image_count, 1)
    
    def test_image_list(self):
        """Test listing images in a folder."""
        # Create a test image first
        with open(self.temp_image_path, 'rb') as img_file:
            image = Image(folder=self.folder)
            image.image_file.save('test_image.png', SimpleUploadedFile('test_image.png', img_file.read()))
        
        # Add namespace to URL name
        url = reverse('imagehub:image-list', kwargs={'folder_identifier': self.folder.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class ErrorHandlingTest(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_nonexistent_folder(self):
        """Test that accessing a nonexistent folder returns 404."""
        # Add namespace to URL name
        url = reverse('imagehub:folder-detail', kwargs={'folder_identifier': 'nonexistent'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)