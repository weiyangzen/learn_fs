# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/TestOMResponse.java

Purpose: Unit-tests large-response warning behavior in `OzoneManagerProtocolServerSideTranslatorPB`. It builds a real `OmMetadataManagerImpl` around a temporary OM DB and mock `OzoneManager`/Ratis dependencies, then verifies the translator's response-size logging helper.

Important APIs/types/functions: Uses `OzoneConfiguration`, `OMConfigKeys.OZONE_OM_DB_DIRS`, `ipc.maximum.response.length`, `OzoneManagerProtocolServerSideTranslatorPB.logLargeResponseIfNeeded`, protobuf `OMResponse`, `ListKeysResponse`, `KeyInfo`, `ProtocolMessageMetrics`, `OMExecutionFlow`, and `GenericTestUtils.LogCapturer`.

Control flow: `setup` creates the metadata manager, configures a 1 MiB IPC max response length, injects mocked OM services, constructs the translator, and captures translator logs. `testLargeResponseLogging` appends 12000 key infos to a list-keys response, records serialized size, invokes the helper, and asserts log text includes the warning, command type, and exact byte count. `testSmallResponseNoLogging` only proves a simple response remains below the warning threshold.

State/persistence: The test initializes an OM RocksDB metadata store in a temp directory but does not mutate tables. Persistent state is limited to DB setup and captured logger output.

Dependencies/integration: Integrates OM protocol protobufs, HDDS replication enum values, the server-side translator, OM execution flow setup, and test log capture. The translator depends on retry-cache and protocol metrics mocks being present.

Risks/test signals: The large test is sensitive to serialized protobuf sizing and the configured response threshold. The small-response test does not invoke the logger, so it only signals threshold math, not absence of logging. Main regression signal is that response-size diagnostics still include command and exact size for oversized OM responses.
