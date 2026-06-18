<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/OMAdmin.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/OMAdmin.java

Purpose: Root Picocli subcommand for Ozone Manager administration and factory for OM protocol clients used by child commands.

Important APIs and types: `AdminSubcommand`, `@MetaInfServices`, `OzoneAdmin`, `OzoneManagerProtocolClientSideTranslatorPB`, `OzoneManagerProtocolPB`, `Hadoop3OmTransportFactory`, `OmTransport`, `OzoneConfiguration`, `UserGroupInformation`, `OZONE_OM_ADDRESS_KEY`, `OZONE_OM_SERVICE_IDS_KEY`, and `ClientId`.

Control flow: Picocli registers OM subcommands for finalization, list-open-files, roles, prepare/cancelprepare, decommission, Ranger sync, leader transfer, key fetch, lease, and snapshot operations. `createOmClient` sets a direct OM host if supplied, otherwise resolves a service ID or requires exactly one configured service ID. It configures the protobuf RPC engine, creates an OM transport, and returns a client translator. With `forceHA`, a non-HA service ID causes an `OzoneClientException`.

State and persistence behavior: It does not persist state. It can mutate the passed `OzoneConfiguration` by setting `ozone.om.address` when a host is provided. Runtime state includes the parent `OzoneAdmin`.

Dependencies and integration points: Service-provider registration makes `om` available to `ozone admin`. All OM child commands depend on this class for parent config/user and client creation.

Risks: Host mode intentionally nulls service ID and mutates config. Ambiguous zero-or-many service IDs without explicit service ID throw. The force-HA branch is used by HA-only commands and can reject otherwise valid host-mode usage.

Test signals: Validate subcommand registration, direct-host override, single service ID inference, ambiguity failure, forceHA rejection, and RPC engine/transport creation paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/OMAdmin.java -->
