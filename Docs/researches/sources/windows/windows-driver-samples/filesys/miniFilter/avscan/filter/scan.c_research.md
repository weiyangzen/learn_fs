# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/scan.c

Scan execution module for both kernel-mode and user-mode scanning. It implements the toy signature scanner, section mapping for kernel scans, user-mode scan notification/wait/abort handling, and section cleanup wrappers.

Key responsibilities:
- `AvScanMemoryStream` decodes the XOR-obfuscated default signature from `avlib.h` and linearly searches a memory range, returning infected, clean, or undetermined if canceled.
- `AvMapSectionAndScan` opens the current process, maps the data-scan section read-only, scans up to the lesser of mapped size and file size, then unmaps/closes.
- `AvScanInKernel` creates a section context and data-scan section, maps/scans it in kernel path, updates stream state, and finalizes the section.
- `AvScanInUser` allocates a scan context, inserts it into the global scan list, sends an `AvMsgStartScanning` notification, waits for the user service to create/scan/close the section, handles timeout/cancellation, sends abort messages, and removes/releases the scan context.
- `AvCloseSectionForDataScan` clears the scan-context backpointer, dereferences the section object, nulls section fields, and calls `FltCloseSectionForDataScan`.

Timeout behavior:
- User-mode scans use `Globals.LocalScanTimeout` or `Globals.NetworkScanTimeout` based on volume device type.
- If the scan wait fails or times out, the kernel asks user mode to abort and waits briefly for cleanup.
- If abort communication fails or times out, the kernel marks the wait aborted and finalizes scan/section state itself.
- For canceled create scans, the file open is canceled via `AvCancelFileOpen`.

Dependencies:
- Filter Manager data scan APIs, shared protocol types from `avlib.h`, scan context lifecycle from `context.c`, abort messaging from `avscan.c`, and stream state macros from `context.h`.

Research notes:
- The scanner is intentionally simple: a single decoded byte-pattern search.
- `AvScanInKernel` leaks the allocated section context if `FltCreateSectionForDataScan` fails before finalization; this is sample code but noteworthy from a production review perspective.
- `AvScanInUser` is the main path used by `avscan.c`; kernel scan support is present for demonstration.
