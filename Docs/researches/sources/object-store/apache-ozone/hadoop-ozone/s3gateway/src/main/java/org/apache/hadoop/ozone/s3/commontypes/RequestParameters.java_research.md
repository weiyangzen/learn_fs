# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/RequestParameters.java

Purpose: `RequestParameters` wraps JAX-RS query parameters with typed lookup helpers used throughout S3 endpoints and handlers.

Important APIs and flow: `of` creates a `MultivaluedMapImpl`. `get` returns the first value, `get(key, defaultValue)` supplies a default, and `getInt` parses integers or throws S3 `InvalidArgument`. The nested `Mutable` interface and implementation support endpoint tests by setting/unsetting query keys.

State, dependencies, risks, and tests: state is a reference to the underlying mutable `MultivaluedMap`; there is no persistence. It integrates with `EndpointBase.initialization`, bucket listing, multipart handlers, and object subresource handlers. Risks include first-value-only semantics, unhandled long/boolean parsing, and unchecked null `params`. Tests should cover integer parsing failure, defaults, and mutation via `queryParamsForTest`.
