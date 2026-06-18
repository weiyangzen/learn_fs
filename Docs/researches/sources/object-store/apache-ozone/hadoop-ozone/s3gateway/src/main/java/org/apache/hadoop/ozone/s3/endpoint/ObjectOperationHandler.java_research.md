<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectOperationHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectOperationHandler.java

## Purpose
Abstract base for object-operation handlers in the endpoint chain. It gives subresource handlers the same dependency surface as `EndpointBase` and a nullable-response contract for chain-of-responsibility dispatch.

## Important APIs, types, and functions
- Defines package-private `handleDeleteRequest`, `handleGetRequest`, `handleHeadRequest`, and `handlePutRequest` hooks.
- Default hook implementations return `null`, meaning the current handler does not own the request.
- `copyDependenciesFrom` uses `EndpointBase.copyDependenciesTo` so handlers share injected clients, headers, context, metrics, and signature state.

## Control flow
Handlers are called in order by `ObjectOperationHandlerChain`. A handler returns a concrete `Response` when it handles the request; otherwise it returns `null` and the next handler is tried.

## State and persistence behavior
This class stores no request state and performs no persistence. Its main state effect is copying endpoint dependencies into handler instances during endpoint initialization.

## Dependencies and integration points
Integrated by `ObjectEndpoint.init`, object ACL/tagging/multipart handlers, and the auditing wrapper. It depends on `ObjectEndpoint.ObjectRequestContext` to carry request metadata.

## Risks and edge cases
Because `null` means "not handled", a handler that accidentally returns `null` after mutating state could allow a second handler to process the same request. Adding new object subresources must preserve chain order so specific handlers run before the default object handler.

## Test signals
Tests should verify subresource query parameters like `tagging`, `acl`, and multipart parameters route to the intended handler and do not fall through to normal object operations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectOperationHandler.java -->
