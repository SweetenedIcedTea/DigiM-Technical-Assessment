# Image Hub Technical Assessment API Documentation

## Overview

The Image Hub API is a Django REST Framework-based service that enables users to organize and manage digital images. This API allows clients to create folders, upload images to these folders, and retrieve detailed information about images including dimensions, file size, and color type.

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [API Endpoints](#api-endpoints)
3. [Data Models](#data-models)
4. [Error Handling](#error-handling)
5. [Libraries and Dependencies](#libraries-and-dependencies)
6. [Development and Testing](#development-and-testing)

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- Pip (Python package manager)
- Virtual environment (recommended)

### Installation Steps

1. Clone the repository:

   ```bash
   git clone [repository-url]
   cd [project-directory]
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`.

## API Endpoints

The base URL for all API endpoints is: `/api/`

### Folders

| Method | Endpoint                            | Description                              | Request Body         | Response                  |
| ------ | ----------------------------------- | ---------------------------------------- | -------------------- | ------------------------- |
| GET    | `/api/folders/`                     | Retrieve all folders                     | None                 | Array of folder objects   |
| POST   | `/api/folders/`                     | Create a new folder                      | `{"name": "string"}` | Created folder object     |
| GET    | `/api/folders/{folder_identifier}/` | Retrieve a specific folder by ID or slug | None                 | Folder object with images |

### Images

| Method | Endpoint                                                      | Description                             | Request Body                | Response                   |
| ------ | ------------------------------------------------------------- | --------------------------------------- | --------------------------- | -------------------------- |
| GET    | `/api/folders/{folder_identifier}/images/`                    | List all images in a folder             | None                        | Array of image objects     |
| POST   | `/api/folders/{folder_identifier}/images/`                    | Upload a new image to a folder          | Form data with `image_file` | Created image object       |
| GET    | `/api/folders/{folder_identifier}/images/{image_identifier}/` | Retrieve a specific image by ID or slug | None                        | Image object with metadata |

### Response Object Examples

#### Folder Object

```json
{
  "id": 1,
  "name": "Vacation Photos",
  "slug": "vacation-photos",
  "created_at": "2023-06-15T10:30:45Z",
  "image_count": 5,
  "images": [
    {
      "id": 1,
      "name": "beach_sunset",
      "slug": "beach-sunset",
      "image_file": "http://example.com/media/uploads/1/beach_sunset.jpg",
      "upload_date": "2023-06-15T10:35:12Z",
      "width": 1920,
      "height": 1080,
      "file_size": 2457600,
      "formatted_file_size": "2.3 MB",
      "is_color": true,
      "url": "http://example.com/media/uploads/1/beach_sunset.jpg"
    }
    // Additional images...
  ]
}
```

#### Image Object

```json
{
  "id": 1,
  "folder": 1,
  "name": "beach_sunset",
  "slug": "beach-sunset",
  "image_file": "http://example.com/media/uploads/1/beach_sunset.jpg",
  "upload_date": "2023-06-15T10:35:12Z",
  "width": 1920,
  "height": 1080,
  "file_size": 2457600,
  "formatted_file_size": "2.3 MB",
  "is_color": true,
  "url": "http://example.com/media/uploads/1/beach_sunset.jpg"
}
```

## Data Models

### Folder

| Field       | Type     | Description                               |
| ----------- | -------- | ----------------------------------------- |
| id          | Integer  | Primary key                               |
| name        | String   | Unique folder name                        |
| slug        | String   | URL-friendly identifier derived from name |
| created_at  | DateTime | When the folder was created               |
| image_count | Integer  | Number of images in the folder            |

### Image

| Field       | Type       | Description                                            |
| ----------- | ---------- | ------------------------------------------------------ |
| id          | Integer    | Primary key                                            |
| folder      | ForeignKey | Reference to the parent folder                         |
| name        | String     | Image name derived from filename                       |
| slug        | String     | URL-friendly identifier for the image                  |
| image_file  | ImageField | The actual image file                                  |
| upload_date | DateTime   | When the image was uploaded                            |
| width       | Integer    | Image width in pixels                                  |
| height      | Integer    | Image height in pixels                                 |
| file_size   | Integer    | File size in bytes                                     |
| is_color    | Boolean    | Whether the image is color (true) or grayscale (false) |

## Error Handling

The API returns standard HTTP status codes to indicate success or failure:

| Status Code | Description                                        |
| ----------- | -------------------------------------------------- |
| 200         | OK - Request succeeded                             |
| 201         | Created - Resource created successfully            |
| 400         | Bad Request - Invalid request format or parameters |
| 404         | Not Found - Resource not found                     |
| 500         | Internal Server Error - Server-side error          |

Error responses include a descriptive message:

```json
{
  "error": "Folder not found",
  "detail": "A folder with the identifier 'nonexistent' does not exist."
}
```

## Libraries and Dependencies

| Library               | Version | Purpose                  |
| --------------------- | ------- | ------------------------ |
| Django                | 5.1.x   | Web framework            |
| Django REST Framework | 3.14.x  | REST API toolkit         |
| Pillow                | 10.0.x  | Image processing library |
| Python                | 3.12.x  | Programming language     |

## Development and Testing

### Running Tests

To run the test suite:

```bash
python manage.py test
```

### Code Coverage

To generate a code coverage report:

```bash
coverage run --source='.' manage.py test
coverage report
```

### Development Guidelines

1. Follow PEP 8 style guidelines for Python code
2. Include docstrings for all functions and classes
3. Add appropriate type hints
4. Write unit tests for new features
5. Run tests before submitting pull requests

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
