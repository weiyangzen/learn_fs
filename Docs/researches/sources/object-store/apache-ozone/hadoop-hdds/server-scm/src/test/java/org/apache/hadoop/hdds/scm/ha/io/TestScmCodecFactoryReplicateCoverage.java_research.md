# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/io/TestScmCodecFactoryReplicateCoverage.java

Purpose: reflective coverage test that catches missing `ScmCodecFactory` registrations for parameters of `@Replicate` APIs, plus a focused encode/decode regression for a container-state transition method.

Important APIs and types: `replicateHandlerTypes()` enumerates replicated SCM handler interfaces. `replicateApisRegisterParameterCodecsInScmCodecFactory()` scans every public method with `@Replicate`, inspects each `Parameter.getParameterizedType()`, and calls `ScmCodecFactory.resolve()` plus `getCodec()` on concrete classes and collection type arguments. `assertTypeResolvable()` handles `Class`, `ParameterizedType`, and upper-bounded `WildcardType`. The second test builds an `SCMRatisRequest` for `RequestType.CONTAINER` and `transitionDeletingOrDeletedToTargetState`.

Control flow: codec failures are accumulated into a multi-line error list rather than failing on the first missing type, giving maintainers a complete registration gap list. Collection generics are recursively validated before the raw collection codec is checked.

State and persistence: no disk state. The test reflects live class metadata and exercises SCM Ratis request serialization into a Ratis `Message`.

Integration points and risks: it protects Ratis replication paths that ordinary mocked tests can miss because mocks often bypass `SCMRatisRequest.encode()`. The handler type list is manual, so new replicated interfaces must be added. Generic inspection is limited to collection-style parameters and resolvable class bounds, so complex nested generic shapes could need extension.
