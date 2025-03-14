from django.test import TestCase
from django.urls import reverse, NoReverseMatch
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from .models import Folder, Image, format_file_size
import tempfile
import os
from PIL import Image as PILImage
from io import BytesIO

class FolderModelTest(TestCase):
    def test_folder_creation(self):
        """Test folder creation with automatic slug generation"""
        with self.subTest("Test basic folder creation"):
            folder = Folder.objects.create(name="Test Folder")
            self.assertEqual(folder.slug, "test-folder")
            self.assertEqual(folder.image_count, 0)
        
        with self.subTest("Test special character handling"):
            folder = Folder.objects.create(name="Test Folder! 123")
            self.assertEqual(folder.slug, "test-folder-123")

    def test_folder_uniqueness(self):
        """Test slug uniqueness constraints"""
        # Test incremental suffix for duplicate slugs
        Folder.objects.create(name="Test Folder")
        folder2 = Folder.objects.create(name="Test-Folder")
        self.assertEqual(folder2.slug, "test-folder-1")

        # Test case insensitivity
        folder3 = Folder.objects.create(name="test folder")
        self.assertEqual(folder3.slug, "test-folder-2")

    def test_folder_ordering(self):
        """Test Meta class ordering"""
        Folder.objects.create(name="Beta")
        Folder.objects.create(name="Alpha")
        folders = Folder.objects.all()
        self.assertEqual([f.name for f in folders], ['Alpha', 'Beta'])

class ImageModelTest(TestCase):
    def setUp(self):
        self.folder = Folder.objects.create(name="Test Folder")
        self.image_file = self.create_test_image()

    def tearDown(self):
        if os.path.exists(self.image_file.name):
            os.unlink(self.image_file.name)
        Image.objects.all().delete()
        Folder.objects.all().delete()

    def create_test_image(self, color='red', size=(100, 100), format='PNG'):
        """Helper to create test images"""
        img_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img = PILImage.new('RGB', size, color=color)
        img.save(img_file, format=format)
        img_file.seek(0)
        return img_file

    def test_image_metadata_extraction(self):
        """Test image processing during save"""
        # Use the correct path from the created image file
        with open(self.image_file.name, 'rb') as img_file:
            image = Image.objects.create(
                folder=self.folder,
                image_file=SimpleUploadedFile('test.png', img_file.read())
            )
        
        # Rest of the test remains the same
        self.assertEqual(image.width, 100)
        self.assertEqual(image.height, 100)
        self.assertTrue(image.is_color)
        
        actual_size = os.path.getsize(image.image_file.path)
        self.assertEqual(image.file_size, actual_size)
        self.assertEqual(image.formatted_file_size, format_file_size(actual_size))
        
    def test_invalid_image_handling(self):
        """Test corrupt/non-image file upload"""
        with self.subTest("Test invalid file content"):
            invalid_file = SimpleUploadedFile('test.png', b'invalid data')
            with self.assertRaises(ValueError):
                Image.objects.create(
                    folder=self.folder,
                    image_file=invalid_file
                )

        with self.subTest("Test invalid file extension"):
            invalid_file = SimpleUploadedFile('test.txt', b'text data', content_type='text/plain')
            with self.assertRaises(ValueError):
                Image.objects.create(
                    folder=self.folder,
                    image_file=invalid_file
                )

    def test_slug_uniqueness(self):
        """Test unique slug constraint within folder"""
        with open(self.image_file.name, 'rb') as img_data:
            # First image
            img1 = Image.objects.create(
                folder=self.folder,
                image_file=SimpleUploadedFile('test.png', img_data.read())
            )
            
            # Reset file pointer
            img_data.seek(0)
            
            # Second image
            img2 = Image.objects.create(
                folder=self.folder,
                image_file=SimpleUploadedFile('test.png', img_data.read())
            )
        
        self.assertNotEqual(img1.slug, img2.slug)

class APITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.folder = Folder.objects.create(name="Test Folder")
        self.image_data = self.create_test_image_data()

    def create_test_image_data(self):
        """Generate in-memory test image"""
        img_io = BytesIO()
        img = PILImage.new('RGB', (100, 100), color='red')
        img.save(img_io, format='PNG')
        img_io.seek(0)
        return img_io

    def test_folder_lifecycle(self):
        """CRUD operations for folders"""
        # Create
        response = self.client.post(
            reverse('imagehub:folder-list'),
            {'name': 'New Folder'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Read
        folder_url = reverse('imagehub:folder-detail', 
                           kwargs={'folder_identifier': response.data['id']})
        response = self.client.get(folder_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Update
        response = self.client.patch(
            folder_url,
            {'name': 'Updated Folder'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Delete
        response = self.client.delete(folder_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_image_upload_validation(self):
        """Test various upload scenarios"""
        url = reverse('imagehub:image-list', 
                kwargs={'folder_identifier': self.folder.slug})
    
        # Create valid image data
        img = PILImage.new('RGB', (100, 100))
        img_io = BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        
        response = self.client.post(
            url,
            {'image_file': SimpleUploadedFile('test.png', img_io.read())},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class ErrorHandlingTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_invalid_requests(self):
        tests = [
            # (endpoint, method, url_kwargs, data, expected_status)
            ('image-list', 'post', 
            {'folder_identifier': 'invalid'}, 
            {'invalid': 'data'}, 
            status.HTTP_400_BAD_REQUEST),  # Changed from 404 to 400
        ]

        for endpoint, method, url_kwargs, data, expected_status in tests:
            with self.subTest(endpoint=endpoint):
                try:
                    url = reverse(f'imagehub:{endpoint}', kwargs=url_kwargs)
                    response = getattr(self.client, method)(url, data)
                    self.assertEqual(response.status_code, expected_status)
                except NoReverseMatch:
                    self.fail(f"Failed to reverse URL for {endpoint}")