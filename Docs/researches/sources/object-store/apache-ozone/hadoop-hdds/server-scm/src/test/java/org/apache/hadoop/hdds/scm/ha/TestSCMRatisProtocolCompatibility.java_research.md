<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisProtocolCompatibility.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisProtocolCompatibility.java

Purpose: This suite validates wire compatibility between legacy proto2 and current proto3 definitions of `SCMRatisProtocol` requests and responses.

Important APIs and types: It uses production `SCMRatisProtocol`, test-only `Proto2SCMRatisProtocolForTesting`, proto2 and Ratis-shaded proto3 `ByteString`, `UnsafeByteOperations`, Java `Random`, and helper methods from `SCMRatisProtocolCompatibilityTestUtil`.

Control flow: The tests generate proto2 requests for each legacy request type and 0-2 arguments, parse them with proto3, verify presence and values, compare string/debug forms, and round-trip back to proto2. Response tests do the same with random proto2 responses. The reverse direction builds proto3 requests/responses, skips default/UNRECOGNIZED request types that cannot satisfy proto2 required fields, parses with proto2, verifies fields, and round-trips back to proto3. `testRequestType` ensures enum numbers and names match.

State and persistence behavior: There is no persistence. Test state is random small strings, integers, byte arrays, method names, request types, and encoded protobuf bytes.

Dependencies and integration points: This is a compatibility anchor for SCM HA/Ratis rolling upgrades where old and new SCMs may exchange replicated method calls and responses.

Risks: Random coverage is small per run, so it guards schema compatibility more than value-space exhaustion. Presence semantics are important because proto3 optional fields must preserve proto2 required data.

Test signals: Successful parse both directions, matching enum numbers, matching method/argument/response byte values, equal short debug strings, and exact round-trip message equality.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisProtocolCompatibility.java -->
