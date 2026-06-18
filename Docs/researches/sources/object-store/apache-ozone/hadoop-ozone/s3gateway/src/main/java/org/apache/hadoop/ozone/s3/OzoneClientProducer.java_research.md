# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/OzoneClientProducer.java

Purpose: `OzoneClientProducer` provides an `OzoneClient` to CDI/JAX-RS endpoint instances for each request while reusing the singleton cached client.

Important APIs and flow: `createClient()` pulls the shared client from `OzoneClientCache` and exposes it with `@Produces`. On request destruction, `destroy()` clears thread-local S3 auth from the client's proxy.

State, dependencies, risks, and tests: state is the request-scoped `client` reference, not an owned connection. It depends on CDI request scope and `OzoneClientCache`. The main risk is leaking per-request S3 auth if `@PreDestroy` does not run or if `client` is null after producer failure. Test signal is endpoint operations using different credentials without cross-request auth contamination.
