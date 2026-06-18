## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/client/TestHddsClientUtils.java

**Purpose:** Validates SCM endpoint resolution, Ozone resource/key name validation, secure exception messages, and throwable-chain lookup helpers in `HddsClientUtils` and related HDDS utility paths.

**Important APIs/types/functions:** `testMissingScmClientAddress()` expects `ConfigurationException` when no SCM client endpoint exists. `testGetScmClientAddress()` covers host-only and host:port parsing. `testGetScmClientAddressForHA()` configures an SCM service ID, node list, per-node client ports, and per-node addresses, then verifies the resolved collection. Fallback tests cover `OZONE_SCM_CLIENT_ADDRESS_KEY`, `OZONE_SCM_NAMES`, and block-client address derivation via `SCMNodeInfo.buildNodeInfo`. `testVerifyResourceName()` and length-specific helpers assert valid bucket/volume-like names and rejection of IP addresses, dot/dash adjacency, uppercase, leading/trailing dots, and unicode fullwidth characters. `testNameTooLongCapped()` and `testInvalidCharactersNotReported()` verify log-safe exception messages. `testVerifyKeyName()` enumerates invalid and valid key characters, including the filesystem copy temp suffix. `testContainsException()` validates cause-chain search.

**Control flow:** Endpoint tests exercise precedence and fallback branches. Name tests exercise validation branches for length, syntax, invalid characters, and sanitized reporting. Throwable tests traverse nested causes until a matching class is found or absent.

**State and persistence:** Uses fresh `OzoneConfiguration` instances. No persistent state, but the tested configuration keys are externally persisted in deployment configs.

**Dependencies and integration points:** Uses `HddsUtils`, `HddsClientUtils`, `SCMNodeInfo`, `ConfUtils`, Hadoop `NetUtils`, Ozone constants, AssertJ, and JUnit. It protects client bootstrap behavior and object namespace validation used by user-facing APIs.

**Risks:** Endpoint resolution is sensitive to HA key suffixing and default-port semantics; tests document that some fallback ports embedded in source keys are ignored. Exception message sanitation is security relevant because invalid user-provided names can reach logs.

**Test signals:** Strong regression signal for SCM address parsing and namespace validation. It does not test DNS resolution, multiple service IDs, or all possible Unicode/control-character cases.
