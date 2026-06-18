# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketOperationHandler.java

Purpose: `BucketOperationHandler` is the abstract base for bucket subresource handlers in a chain-of-responsibility design.

Important APIs and flow: default `handlePutRequest`, `handleGetRequest`, and `handleDeleteRequest` return null, signaling "not responsible". `copyDependenciesFrom` copies endpoint dependencies from an `EndpointBase`, enabling handlers created manually in `BucketEndpoint.init()` to use CDI-provided config/client/context fields.

State, dependencies, risks, and tests: state is inherited endpoint dependency state. It integrates with `BucketOperationHandlerChain`, concrete ACL/CRUD/location/multipart handlers, and auditing wrappers. Risks include handlers forgetting to return null for unclaimed requests or failing to set action before returning/throwing. Tests should verify dependency copying and chain fall-through semantics.
