# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmCodecFactory.java

Purpose: Singleton registry that maps SCM HA request/response parameter and return types to serialization codecs and resolves subclasses to supported base types.

Important APIs and types: Registers generated protobuf messages, primitives/wrappers, strings, booleans, `BigInteger`, certificates, shaded and non-shaded `ByteString`, `ManagedSecretKey`, protobuf enums, and `List`. Public methods are `getInstance`, `resolve(String)`, `resolve(Class<?>)`, `getCodec`, and `getClass`. Inner `ClassResolver` handles assignable-type lookup and caches resolutions.

Control flow: Constructor populates exact codecs, then builds a resolver from known types, then adds list codec. Resolution first checks provided exact class names, then cached values, then loads the class and finds an assignable registered base.

State and persistence behavior: Runtime singleton state includes codec maps and class-resolution caches. No direct persistence, but serialized forms become Ratis log payloads.

Dependencies and integration points: Central to `SCMRatisRequest` and `SCMRatisResponse`, generated invokers, and all HA codecs.

Risks and test signals: Adding a replicated API parameter requires factory support. List codec assumes homogeneous lists and infers element type from the first element. Tests should cover exact and subclass resolution, unknown classes, unknown codecs, enum mapping, list handling, and shaded/non-shaded protobuf classes.
