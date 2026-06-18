<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-proxy-remove.go -->
# sources/object-store/minio-mc/cmd/support-proxy-remove.go

Purpose: implements `mc support proxy remove TARGET`, deleting the configured SUBNET proxy from a MinIO cluster.

Important APIs/types/functions: `supportProxyRemoveCmd`, `supportProxyRemoveMessage`, `checkSupportProxyRemoveSyntax`, and `mainSupportProxyRemove`.

Control flow: the command validates exactly one argument, sets success color, extracts the alias, requires registration, creates an admin client via `getClient`, calls `DelConfigKV(globalContext, "subnet proxy")`, and prints a success message.

State and persistence: persistent mutation is remote server config deletion for the `subnet proxy` key. No local state is written.

Dependencies and integration points: part of `support proxy`; uses shared support registration and output helpers plus MinIO admin config deletion.

Risks and test signals: behavior depends on server support for the subnet config subsystem and caller permissions. Tests should cover argument count, successful JSON/text output, and delete failure handling.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-proxy-remove.go -->
