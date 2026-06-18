# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/filter/mspyLib.c

Kernel-mode support library for the MiniSpy minifilter’s logging path.

Key responsibilities:
- Allocates, initializes, frees, queues, drains, and returns variable-length `LOG_RECORD` entries.
- Converts transaction notification bit flags into MiniSpy minor-code values with `TxNotificationToMinorCode`.
- Captures pre-operation, post-operation, and transaction-notification metadata into shared `RECORD_DATA`.
- Copies record batches to user buffers in `SpyGetLog`, preserving records if a user-buffer copy faults.
- Reads registry parameters `MaxRecords` and `NameQueryMethod` into `MiniSpyData`.
- On Vista/Win7 builds, parses Extra Create Parameters and formats known ECP details into the log name buffer.

Important behavior:
- Uses a nonpaged lookaside list plus `MiniSpyData.RecordsAllocated` to cap log-buffer allocations.
- Falls back to a single static out-of-memory buffer when dynamic allocation fails or the memory allowance is exceeded.
- Protects `MiniSpyData.OutputBufferList` with a spin lock and releases it before copying records to user mode.
- Ensures variable log record sizes are pointer-aligned to avoid IA64 alignment faults.
- If no file name is present, `SpyGetLog` appends an empty null-terminated name before returning the record.

ECP handling:
- `SpyParseEcps` walks FltMgr ECP lists, counts total ECPs, ignores user-mode-originated known ECP contexts, and records known ECP flags.
- `SpyBuildEcpDataString` formats prefetch, oplock-key, NFS-open, and SRV-open ECP data when supported by build flags.
- Network ECPs format IPv4/IPv6 socket addresses with `RtlIpv4AddressToStringEx` / `RtlIpv6AddressToStringEx`.

Dependencies and risks:
- Depends on global `MiniSpyData`, shared structures from `minispy.h`, kernel filter-manager APIs, and MiniSpy kernel declarations from `mspyKern.h`.
- Allocation-limit checks are intentionally approximate; concurrent callers can transiently exceed the configured maximum.
- The single static fallback buffer is guarded by `InterlockedExchange`, but release sets the flag with a plain store.
- `_snwprintf` truncation is handled manually, and the code relies on the shared record-size macros to keep output bounded.
