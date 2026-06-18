# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/BucketOperationHandlerChain.java

Purpose: `BucketOperationHandlerChain` dispatches bucket requests to the first handler that claims them.

Important APIs and flow: for DELETE, GET, and PUT it loops through handlers in insertion order, returning the first non-null `Response`. The builder copies dependencies from the owning `BucketEndpoint` into each added handler and into the final chain.

State, dependencies, risks, and tests: state is an ordered list of handlers. It integrates with `BucketEndpoint.init`, where location, ACL, multipart listing, CRUD, and fallback endpoint handlers are ordered deliberately. Risks include ordering changes causing broad handlers to preempt specific subresources, null response after all handlers, and dependency copy timing. Tests should cover ordering and fallback for each subresource.
