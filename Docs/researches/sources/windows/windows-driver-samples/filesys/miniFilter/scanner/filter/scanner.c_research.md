# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/scanner/filter/scanner.c

Kernel-mode scanner minifilter sample that asks a user-mode service whether scanned data is safe.

Key responsibilities:
- Registers create, cleanup, write, and Win8+ file-system-control callbacks.
- Registers a stream-handle context containing `RescanRequired`.
- Creates secured communication port `\\ScannerPort`, limited to one client.
- Reads the `Extensions` registry multi-string from the service `Parameters` key and falls back to scanning `.doc` if unavailable.
- Scans target files on open, scans write buffers before regular writes complete, rescans write-opened files on cleanup, and blocks offload writes for interested handles.

Initialization and configuration:
- `DriverEntry` opts into `NonPagedPoolNx`, registers with FltMgr, initializes scanned extensions, builds a default admin/system security descriptor, creates the communication port, then starts filtering.
- `ScannerOpenServiceParametersKey` prefers `IoOpenDriverRegistryKey` when available and falls back to manually opening the service `Parameters` subkey.
- `ScannerInitializeScannedExtensions` reads `Extensions`, counts REG_MULTI_SZ entries, allocates an array of `UNICODE_STRING`s, and copies each extension.
- `ScannerFreeExtensions` releases configured extension strings and handles the static default extension specially.

I/O behavior:
- `ScannerPreCreate` skips post-create scanning for the trusted connected user process.
- `ScannerPostCreate` ignores failed/reparse creates, gets normalized name info, checks extension match, reads/scans the file through user mode, denies open with `FltCancelFileOpen` on unsafe content, and marks write-access handles for cleanup rescan.
- `ScannerPreCleanup` rescans handles whose stream-handle context requires it and logs unsafe detection.
- `ScannerPreWrite` sends up to `SCANNER_READ_BUFFER_SIZE` bytes from the write buffer to user mode; unsafe nonpaging writes are completed with `STATUS_ACCESS_DENIED`.
- `ScannerPreFileSystemControl` blocks `FSCTL_OFFLOAD_WRITE` for interested handles because the sample cannot inspect offloaded data.
- `ScannerpScanFileInUserMode` reads the beginning of the file with noncached aligned I/O and sends it to the user service.

Communication model:
- `ScannerPortConnect` stores the client port and current process as trusted `UserProcess`.
- `ScannerPortDisconnect` closes the client port and clears `UserProcess`.
- `FltSendMessage` uses the same notification buffer as the reply storage; reply length is `sizeof(SCANNER_REPLY)`.

Dependencies and risks:
- Depends on `scanuk.h` shared messages, `scanner.h` globals/context, FltMgr communication ports, stream-handle contexts, and file-name parsing.
- Failing to contact user mode generally allows opens/writes, avoiding bootstrapping failures but weakening enforcement.
- The sample explicitly notes that large nonpaged allocations and scanning only the first chunk are not production-quality.
- Memory-mapped writes are not blocked in the write path; cleanup scanning can only detect after the fact.
- Registry parsing does not deeply validate the value type/format beyond query success.
