# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/inc/avlib.h

Shared kernel/user protocol header for the AV scan sample. It defines port names, command/message enums, message payload structures, connection context, invalid section handle sentinel, and the toy signature pattern.

Key definitions:
- Port names: scan, abort, and query Filter Manager communication ports.
- `AVSCAN_COMMAND`: query file modified, create section for data scan, close section for data scan.
- `AVSCAN_MESSAGE`: start scanning, abort scanning, filter unloading.
- `AVSCAN_REASON`: scan on open or cleanup.
- `AVSCAN_RESULT`: undetermined, infected, clean.
- `COMMAND_MESSAGE`: user-to-kernel command with scan ID, scan thread ID, and union for file handle or scan result.
- `AV_SCANNER_NOTIFICATION`: kernel-to-user notification with message, reason, scan ID, and scan thread ID.
- `AVSCAN_CONNECTION_TYPE` and `AV_CONNECTION_CONTEXT`: identify scan/abort/query client connections.
- `AV_DEFAULT_SEARCH_PATTERN`, size, and XOR key for the sample signature string.

Dependencies:
- Designed to compile in both user and kernel mode; uses Windows handle-sized types and suppresses MSVC nameless union warning.

Research notes:
- This header is the protocol contract between `filter/communication.c`, `filter/scan.c`, and user-mode scanner code.
- The default pattern is obfuscated with XOR key `90`; scan code decodes it before searching.
