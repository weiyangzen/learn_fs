<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/ListOpenFilesSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/ListOpenFilesSubCommand.java

Purpose: Lists open OM keys/files, with paging, path-prefix filtering, optional JSON output, and optional inclusion of hsync-deleted or hsync-overwritten open-key records.

Important APIs and types: `OzoneManagerProtocol.getServiceInfo()`, `RpcClient.getOmVersion`, `OzoneManagerVersion.HBASE_SUPPORT`, `listOpenFiles`, `ListOpenFilesResult`, `OpenKeySession`, `OmKeyInfo`, `OzoneConsts` hsync metadata keys, `JsonUtils`, and `OmAddressOptions.OptionalServiceIdOrHostMixin`.

Control flow: `call()` opens an OM client and delegates to `execute`. The command rejects old OM versions by printing an error and returning. It calls `listOpenFiles(pathPrefix, limit, startItem)`, removes deleted or overwritten hsync records unless requested, and then prints either full JSON or a human table-like listing. Human output includes total count, shown count, path prefix, optional continuation token, client ID, creation time, hsync/deleted/overwritten columns, full key path, and a next-batch command if `hasMore()` is true.

State and persistence behavior: Read-only local behavior. It mutates the returned `ListOpenFilesResult.getOpenKeys()` list in memory when filtering. Continuation state is represented by the server-returned token and printed command, not stored.

Dependencies and integration points: Uses OM protocol list-open-files support, OM version gating for HBase support, Ozone key metadata conventions, and OM address `toString()` to reconstruct a follow-up CLI command.

Risks: Filtering mutates the response object before JSON output, so JSON respects CLI filters rather than server raw output. `HSYNC_CLIENT_ID` is parsed as a long only when `isHsync()` is true; malformed metadata can fail output. The next-batch command does not shell-quote path prefixes or start tokens.

Test signals: Cover version-gate errors, deleted/overwritten filtering, hsync client ID display, JSON vs human output, continuation command generation, limit/prefix/start parsing, and full path formatting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/ListOpenFilesSubCommand.java -->
