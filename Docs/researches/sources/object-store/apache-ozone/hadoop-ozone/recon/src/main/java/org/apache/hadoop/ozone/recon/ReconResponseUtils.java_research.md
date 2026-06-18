# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconResponseUtils.java

## Purpose
`ReconResponseUtils` provides small helpers for building common JSON error or empty-result HTTP responses.

## Important APIs, Types, And Functions
Static APIs are `noMatchedKeysResponse(String)`, `createBadRequestResponse(String)`, and `createInternalServerErrorResponse(String)`. Each returns a JAX-RS `Response` with JSON media type.

## Control Flow
Each helper formats a JSON string with a message, sets the HTTP status (`204`, `400`, or `500`), applies `MediaType.APPLICATION_JSON`, and builds the response.

## State And Persistence
The class is stateless and has a private constructor.

## Dependencies And Integration Points
Endpoints can use these helpers for consistent response bodies. It depends only on JAX-RS `Response` and `MediaType`.

## Risks
Messages are inserted via `String.format` without JSON escaping, so quotes or control characters in user-provided input can produce invalid JSON. A `204 NO_CONTENT` response with an entity is unusual and may be stripped by clients or servers.

## Test Signals
Tests should assert status codes, media type, body content for simple messages, and escaping behavior or lack thereof for special characters.
