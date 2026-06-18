<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/GetServiceRolesSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/GetServiceRolesSubcommand.java

Purpose: Lists OM service members and their Ratis roles in plain text, JSON, or table form.

Important APIs and types: `OzoneManagerProtocol.getServiceList()`, `ServiceInfo`, `OMRoleInfo`, `HddsProtos.NodeType.OM`, `JsonUtils`, `FormattingCLIUtils`, and Picocli `--json`/`--table` options.

Control flow: `call()` opens an OM client. JSON output maps each OM node ID to `serverRole` and `hostname`; table output adds rows under `Host Name`, `Node ID`, and `Role`; default output prints `nodeId : role (hostname)`. Non-OM service entries and entries with null OM role info are skipped.

State and persistence behavior: Read-only. It formats a service-list snapshot returned by OM and does not mutate local or remote state.

Dependencies and integration points: Registered as `roles` with alias `getserviceroles`; depends on OM service discovery and Ratis role reporting.

Risks: `--json` and `--table` are independent booleans; JSON wins if both are set. The JSON shape is a list of single-entry maps, which clients may depend on even though it is awkward for lookup.

Test signals: Verify filtering of non-OM entries, all three output formats, option precedence, empty lists, and stable table headers/JSON keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/GetServiceRolesSubcommand.java -->
