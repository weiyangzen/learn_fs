<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/mdsearch.c -->
# sources/user-network-fs/samba/source3/utils/mdsearch.c

## Purpose
`mdsearch.c` is a command-line client for Samba's Spotlight/metadata search service (`mdssvc`). It connects to a server over SMB IPC, opens the mdssvc RPC pipe, runs a metadata query for a share/path, and prints matching paths.

## Important APIs, types, and functions
- Global options `opt_path` and `opt_live` select server-relative base path and live query mode.
- `main()` handles all behavior: Samba command-line and credential setup, full IPC connection, mdssvc RPC pipe opening, `mdscli_connect`, search creation, result polling, path lookup, close, and disconnect.

## Control flow
The program parses options and positional `<server> <share> <query>`, strips leading `//` or `\\` from the server, initializes tevent and messaging, obtains credentials, connects to `IPC$`, opens the mdssvc RPC pipe without auth, and creates an mdssvc client context for the target share. It chooses a base path from `--path` or `mdscli_get_basepath()`, starts the search, sleeps briefly for non-live searches, then repeatedly calls `mdscli_get_results()`. CNIDs are resolved to paths with `mdscli_get_path()` and printed. Non-live searches stop on no more matches; live searches poll indefinitely.

## State and persistence behavior
The utility is mostly read-only from the client's perspective, but it creates server-side mdssvc search state that is closed with `mdscli_close_search()` and a service context closed with `mdscli_disconnect()`. It does not persist local files.

## Dependencies and integration points
It integrates with Samba command-line credentials, SMB client full connection, transport parsing, IPC tree connect, RPC client pipe code, generated mdssvc NDR table, and `rpc_client/cli_mdssvc.h` helpers. It relies on the server exposing mdssvc for the target share.

## Risks and edge cases
- Usage validation checks `server == NULL || mds_query == NULL` but does not explicitly require `share != NULL` before passing it to mdssvc.
- Live mode is an infinite polling loop until interrupted.
- It opens the mdssvc pipe with noauth after authenticating the SMB connection; server policy must allow that pipe behavior.
- Errors after messaging initialization must free global command-line messaging context, which the fail labels handle.

## Test signals
Integration tests require a Samba server with mdssvc enabled and indexed content. Expected signals are successful query results, no-more-matches handling for non-live mode, and stable path resolution for returned CNIDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/mdsearch.c -->
