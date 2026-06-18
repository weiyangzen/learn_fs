<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/ScmAdmin.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/ScmAdmin.java

Purpose: Root Picocli subcommand for Storage Container Manager administration.

Important APIs and types: `AdminSubcommand`, `@MetaInfServices`, parent `OzoneAdmin`, and registered subcommands for roles, finalization, transfer, decommission, key rotation, and deleted-block transaction operations.

Control flow: Picocli wires the `scm` namespace and injects the parent command. `getParent()` exposes root configuration and user access to child commands.

State and persistence behavior: No persistence. Runtime state is just the parent reference.

Dependencies and integration points: Service-provider registration exposes the SCM admin command to the Ozone admin CLI.

Risks: Child command availability depends on this static subcommand list. There is no direct client factory here; most SCM child commands rely on `ScmSubcommand` or their own `ScmOption`.

Test signals: Service-loader registration, help/subcommand listing, and parent injection for children.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/ScmAdmin.java -->
