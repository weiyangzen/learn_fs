
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/EndpointTestUtils.java

Purpose: helper methods for endpoint unit tests, especially object GET/PUT/DELETE, tagging, multipart upload, and error/status assertions.

Important APIs and control flow: methods set query params and mocked HTTP methods/headers before invoking `ObjectEndpoint` methods. Multipart helpers initiate upload, upload parts, build completion requests, and assert response entities/ETags. `assertStatus`, `assertSucceeds`, and `assertErrorResponse` centralize response/error assertions. `FailingInputStream` simulates upload interruption after a configured byte count.

State, dependencies, integration: no global state; it mutates endpoint query params and Mockito stubs supplied by callers. Integrated by multipart/object endpoint tests. Depends on S3 constants, JAX-RS responses, Apache HTTP status, and Ratis checked functional interfaces.

Risks and test signals: helpers can leave query parameters set on reused endpoint instances, so tests must manage endpoint state. Error assertion overload closing a response assumes lazy exception behavior from some endpoint methods.
