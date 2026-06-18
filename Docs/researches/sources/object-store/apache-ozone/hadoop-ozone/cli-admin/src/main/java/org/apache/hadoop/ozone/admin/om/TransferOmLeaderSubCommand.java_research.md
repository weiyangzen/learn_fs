<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/TransferOmLeaderSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/TransferOmLeaderSubCommand.java

Purpose: Manually transfers OM Ratis leadership either to a named OM node ID or to a randomly selected follower.

Important APIs and types: `OzoneManagerProtocol.transferLeadership`, `OmAddressOptions.OptionalServiceIdMixin`, Picocli `ArgGroup`, and nested `TransferOption` with `--new-leader-id` aliases and `--random`.

Control flow: Picocli enforces exactly one transfer mode. `call()` converts random mode to an empty target string, opens an OM client, invokes `transferLeadership`, and prints whether transfer went to a random node or the specified node.

State and persistence behavior: No local persistence. The remote Ratis group leader changes if the server accepts the request.

Dependencies and integration points: Used under `OMAdmin`; relies on OM service ID resolution and OM-side leadership transfer semantics where empty string means random follower.

Risks: The empty-string sentinel is a protocol convention and must stay aligned with OM server logic. There is no post-transfer verification that the target became leader.

Test signals: Verify arg-group exclusivity, random sentinel, explicit node ID, RPC invocation, and success text.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/TransferOmLeaderSubCommand.java -->
