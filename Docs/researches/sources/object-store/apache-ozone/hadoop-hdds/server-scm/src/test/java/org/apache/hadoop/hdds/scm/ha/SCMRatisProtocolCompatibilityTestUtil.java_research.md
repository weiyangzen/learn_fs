<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/SCMRatisProtocolCompatibilityTestUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/SCMRatisProtocolCompatibilityTestUtil.java

Purpose: This utility supports SCM Ratis protocol compatibility tests by constructing random proto2-format method arguments, responses, and requests for the test-only legacy schema.

Important APIs and types: It uses `Proto2SCMRatisProtocolForTesting`, protobuf `ByteString`, `ByteBuffer`, and static random/type fixtures from `TestSCMRatisProtocolCompatibility`. Helpers include `randomValueProto2`, `randomProto2MethodArgument`, `randomProto2SCMRatisResponseProto`, and `proto2Request`.

Control flow: `randomValueProto2` chooses encoding by Java type: UTF-8 digits for `String`, four-byte big-endian integers for `Integer`, and random byte arrays for `byte[]`. Request builders attach a method name, request type, and the requested number of random arguments.

State and persistence behavior: It is stateless except use of the shared random generator. No persistent data is created.

Dependencies and integration points: It feeds `TestSCMRatisProtocolCompatibility`, which verifies wire compatibility between legacy proto2 and current proto3 SCM Ratis protocol definitions.

Risks: Random small values give broad but not exhaustive coverage. The utility must stay aligned with the production/test protocol type list.

Test signals: Utility correctness is observed indirectly through proto2/proto3 round-trip equality in the compatibility tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/SCMRatisProtocolCompatibilityTestUtil.java -->
