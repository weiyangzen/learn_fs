# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMRatisRequest.java

Purpose: Encodes SCM replicated method calls into Ratis `Message` payloads and decodes committed log entries back into typed local invocations.

Important APIs and types: `of`, `encode`, `decode`, `getType`, `getOperation`, `getArguments`, `getParameterTypes`, and `smProtoToString`. It serializes `RequestType`, method name, parameter type names, and argument bytes using `ScmCodecFactory`.

Control flow: Creation verifies parameter count equals argument count. Encoding records declared parameter types, not runtime subclass types, then resolves the codec type and serializes each argument. Decoding validates required proto fields, loads parameter classes by name, resolves codecs, and deserializes argument values.

State and persistence behavior: No local persistence, but encoded bytes become Ratis log data and therefore define the replicated operation format.

Dependencies and integration points: Produced by `ScmInvoker`, consumed by `SCMRatisServerImpl.submitRequest`, `SCMStateMachine.applyTransaction`, and the test stub.

Risks and test signals: Codec coverage and declared parameter types are compatibility-critical. Tests should cover missing proto fields, subclass parameter resolution, lists, enums, generated messages, and debug string handling for malformed state-machine log entries.
