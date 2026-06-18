<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/FetchKeySubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/FetchKeySubCommand.java

Purpose: Implements `ozone admin om fetch-key`, forcing OM to refetch the latest secret key from SCM and reporting the current key UUID.

Important APIs and types: `OmAddressOptions.OptionalServiceIdMixin`, `OzoneManagerProtocol.refetchSecretKey()`, `UUID`, Picocli command metadata, and `Callable<Void>`.

Control flow: The command opens an OM protocol client for the optional service ID, calls `refetchSecretKey`, prints `Current Secret Key ID: <uuid>`, and closes the client.

State and persistence behavior: No local persistence. Remote OM key-manager state may be refreshed from SCM; the returned UUID is only printed.

Dependencies and integration points: Depends on OM-to-SCM secret-key infrastructure and OM protocol support. It is exposed as an `OMAdmin` subcommand.

Risks: It assumes the OM can contact SCM and the caller is authorized. There is no retry or distinction between no-op and newly fetched key beyond the returned UUID.

Test signals: Mock the OM protocol return UUID, verify output formatting, and exercise RPC error propagation and optional service-ID routing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/FetchKeySubCommand.java -->
