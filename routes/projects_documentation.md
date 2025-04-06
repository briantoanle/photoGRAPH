# Projects API Documentation

Base URL: `/api/projects`

## Endpoints

### 1. Get projects by current logged in user
- **URL**: `/`
- **Method**: `GET`
- **Description**: Retrieves all projects for the currently logged-in user
- **Authentication Required**: Yes
- **Response**: Array of project objects
- **Response Format**:
```json
[
  {
    "project_id": "integer",
    "project_name": "string",
    "description": "string",
    "created_at": "timestamp",
    "updated_at": "timestamp"
  }
]
```
- **Error Response** (401):
```json
{
  "error": "Unauthorized"
}
```

### 2. Get All Projects in database
- **URL**: `/getall`
- **Method**: `GET`
- **Description**: Retrieves a list of all projects
- **Response**: Array of project objects
- **Response Format**:
```json
[
  {
    "user": "integer",
    "project_id": "integer",
    "project_name": "string"
  }
]
```

### 3. Get Project by  Project ID
- **URL**: `/getProject/<project_id>`
- **Method**: `GET`
- **Description**: Retrieves a specific project by its ID
- **Parameters**:
  - `project_id` (path parameter): Integer ID of the project
- **Response**: Project object
- **Response Format**:
```json
{
  "user_id": "integer",
  "project_id": "integer",
  "project_name": "string"
}
```

### 4. Get Projects by User ID
- **URL**: `/user/<user_id>`
- **Method**: `GET`
- **Description**: Retrieves all projects for a specific user
- **Parameters**:
  - `user_id` (path parameter): Integer ID of the user
- **Response**: Array of project objects
- **Response Format**:
```json
[
  {
    "user": "integer",
    "project_id": "integer",
    "project_name": "string"
  }
]
```

### 5. Create Project
- **URL**: `/create`
- **Method**: `POST`
- **Description**: Creates a new project
- **Authentication Required**: Yes
- **Request Body**:
```json
{
  "project_name": "string",
  "description": "string"
}
```
- **Validation Rules**:
  - Project name is required
  - Description must not exceed 2000 characters
- **Response** (201):
```json
{
  "message": "Project created successfully",
  "project_id": "integer"
}
```
- **Error Responses**:
  - 400: Missing project name or description too long
  - 401: Unauthorized

### 6. Get Project Details
- **URL**: `/<project_id>`
- **Method**: `GET`
- **Description**: Retrieves detailed information about a specific project
- **Authentication Required**: Yes
- **Parameters**:
  - `project_id` (path parameter): Integer ID of the project
- **Response**: Project object
- **Response Format**:
```json
{
  "project_id": "integer",
  "project_name": "string",
  "description": "string",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```
- **Error Responses**:
  - 401: Unauthorized
  - 404: Project not found

### 7. Update Project Name
- **URL**: `/updateProjectName/<project_id>`
- **Method**: `PUT`
- **Description**: Updates the name of a specific project
- **Authentication Required**: Yes
- **Parameters**:
  - `project_id` (path parameter): Integer ID of the project
- **Request Body**:
```json
{
  "project_name": "string"
}
```
- **Validation Rules**:
  - New project name is required
  - User must own the project
- **Response** (200):
```json
{
  "message": "Project name updated successfully",
  "project_id": "integer"
}
```
- **Error Responses**:
  - 400: Missing project name
  - 401: Unauthorized
  - 404: Project not found or not authorized

### 8. Update Project Description
- **URL**: `/updateProjectDescription/<project_id>`
- **Method**: `PUT`
- **Description**: Updates the description of a specific project
- **Authentication Required**: Yes
- **Parameters**:
  - `project_id` (path parameter): Integer ID of the project
- **Request Body**:
```json
{
  "description": "string"
}
```
- **Validation Rules**:
  - New description is required
  - User must own the project
- **Response** (200):
```json
{
  "message": "Project description updated successfully",
  "project_id": "integer"
}
```
- **Error Responses**:
  - 400: Missing description
  - 401: Unauthorized
  - 404: Project not found or not authorized

## Authentication
- Most endpoints require session-based authentication
- Protected routes require an active user session
- The session is automatically handled through cookies

## Error Handling
All endpoints may return the following HTTP status codes:
- 400: Bad Request (invalid input)
- 401: Unauthorized (not authenticated)
- 404: Not Found
- 500: Database connection failed

## Notes
- All string inputs are automatically trimmed of whitespace
- Project descriptions have a maximum length of 2000 characters
- Projects are associated with the authenticated user who created them
- Timestamps (created_at, updated_at) are automatically managed by the system