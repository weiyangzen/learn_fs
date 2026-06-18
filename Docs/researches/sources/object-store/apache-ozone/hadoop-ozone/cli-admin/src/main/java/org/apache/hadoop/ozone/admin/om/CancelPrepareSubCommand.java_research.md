<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/CancelPrepareSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/CancelPrepareSubCommand.java

Purpose: Implements `ozone admin om cancelprepare`, the administrative escape hatch that clears OM prepare mode after upgrade or downgrade preparation. It is intentionally narrow: resolve an OM HA client from an optional service ID, call `OzoneManagerProtocol.cancelOzoneManagerPrepare()`, and print that write requests can resume.

Important APIs and types: Picocli `@Command` and `@Mixin`, `Callable<Void>`, `OmAddressOptions.OptionalServiceIdMixin`, and `OzoneManagerProtocol`. The command's only behavioral method is `call()`.

Control flow: Picocli populates the OM address mixin. `call()` opens an OM protocol client with try-with-resources, invokes `cancelOzoneManagerPrepare`, prints a success message, closes the client, and returns null. Exceptions are not caught locally, so RPC or configuration failures propagate to the CLI framework.

State and persistence behavior: No local state is persisted. The durable effect is remote OM cluster state: the prepare gate is cancelled so OMs can accept writes again. Runtime state is limited to the client proxy.

Dependencies and integration points: Registered under `OMAdmin`; depends on OM address resolution, Hadoop/Ozone admin root configuration and user, and OM protocol server support for prepare cancellation.

Risks: A misresolved service ID or ambiguous HA configuration can target the wrong OM service or fail before RPC. There is no confirmation prompt or status check after cancellation; success is inferred from the RPC returning.

Test signals: Useful tests mock `OzoneManagerProtocol`, verify `cancelOzoneManagerPrepare()` is called once, check success text, and cover optional service ID resolution and propagated RPC failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/CancelPrepareSubCommand.java -->
