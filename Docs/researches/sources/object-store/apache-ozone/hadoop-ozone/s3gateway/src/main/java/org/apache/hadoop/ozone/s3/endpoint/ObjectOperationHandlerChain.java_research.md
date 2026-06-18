<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectOperationHandlerChain.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectOperationHandlerChain.java

## Purpose
Concrete chain-of-responsibility dispatcher for object operations. It lets object subresource handlers intercept requests before the default `ObjectEndpoint` behavior.

## Important APIs, types, and functions
- Stores ordered `List<ObjectOperationHandler> handlers`.
- Overrides delete/get/head/put hooks and returns the first non-null handler response.
- `newBuilder(ObjectEndpoint)` creates a builder that copies endpoint dependencies into each added handler and the final chain.

## Control flow
Each operation loops through handlers in insertion order. The first handler that recognizes the request, usually by query parameter plus HTTP method, returns a response. If no handler recognizes it, `null` is returned to the caller.

## State and persistence behavior
The chain itself is immutable after construction. Persistence is performed only by downstream handlers. Dependency copying is the stateful initialization step.

## Dependencies and integration points
Constructed by `ObjectEndpoint.init` and wrapped by `AuditingObjectOperationHandler`. It coordinates `ObjectAclHandler`, `ObjectTaggingHandler`, `MultipartKeyHandler`, and `ObjectEndpoint`.

## Risks and edge cases
Incorrect handler ordering changes API behavior. A new handler added after `ObjectEndpoint` may never run because the default endpoint handles broad object operations.

## Test signals
Subresource tests should verify dispatch order by sending ambiguous object requests with query parameters and confirming the expected metrics/action/error path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectOperationHandlerChain.java -->
