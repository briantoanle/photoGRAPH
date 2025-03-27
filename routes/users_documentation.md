# User API Documentation

Base URL: `/api/users`

## Endpoints

### 1. Get All Users
- **URL**: `/`
- **Method**: `GET`
- **Description**: Retrieves a list of all users
- **Response**: Array of user objects
- **Response Format**:
```json
[
  {
    "first_name": "string",
    "last_name": "string",
    "email": "string"
  }
]
```

### 2. Get User by ID
- **URL**: `/<user_id>`
- **Method**: `GET`
- **Description**: Retrieves a specific user by their ID
- **Parameters**:
  - `user_id` (path parameter): Integer ID of the user
- **Response**: User object
- **Response Format**:
```json
{
  "first_name": "string",
  "last_name": "string",
  "email": "string"
}
```
- **Error Response** (404):
```json
{
  "error": "User not found"
}
```

### 3. Register User
- **URL**: `/register`
- **Method**: `POST`
- **Description**: Creates a new user account
- **Request Body**:
```json
{
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "password": "string"
}
```
- **Validation Rules**:
  - Email must be in valid format
  - Password must be at least 6 characters long
  - All fields are required
- **Response** (201):
```json
{
  "message": "User created successfully",
  "user_id": "integer"
}
```
- **Error Responses**:
  - 400: Missing required fields or invalid input
  - 409: Email already exists

### 4. Login User
- **URL**: `/login`
- **Method**: `POST`
- **Description**: Authenticates a user and creates a session
- **Request Body**:
```json
{
  "email": "string",
  "password": "string"
}
```
- **Response**:
```json
{
  "message": "Login successful",
  "user_id": "integer"
}
```
- **Error Response** (401):
```json
{
  "error": "Invalid email or password"
}
```

### 5. Logout User
- **URL**: `/logout`
- **Method**: `POST`
- **Description**: Logs out the current user and destroys their session
- **Response**:
```json
{
  "message": "Logout successful"
}
```

### 6. Get Current User
- **URL**: `/me`
- **Method**: `GET`
- **Description**: Retrieves information about the currently logged-in user
- **Authentication Required**: Yes
- **Response**:
```json
{
  "user_id": "integer"
}
```
- **Error Response** (401):
```json
{
  "error": "Unauthorized"
}
```

## Authentication
- The API uses session-based authentication
- After successful login, a session is created and maintained
- Protected routes require an active session
- The session is automatically handled through cookies

## Error Handling
All endpoints may return the following HTTP status codes:
- 400: Bad Request (invalid input)
- 401: Unauthorized (not authenticated)
- 404: Not Found
- 409: Conflict (e.g., email already exists)

## Notes
- All string inputs are automatically trimmed of whitespace
- Email addresses must be in a valid format
- Passwords are hashed before storage
- Session management is handled automatically through cookies
