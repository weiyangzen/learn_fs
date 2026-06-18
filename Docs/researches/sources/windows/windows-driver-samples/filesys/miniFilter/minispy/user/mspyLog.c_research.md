# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/user/mspyLog.c

User-mode MiniSpy log retrieval and formatting implementation.

Key responsibilities:
- `RetrieveLogRecords` runs as the logging thread, sends `GetMiniSpyLog` commands through the filter communication port, validates packed `LOG_RECORD` lengths, and dumps each record to screen and/or file.
- `TranslateFileTag` recognizes mount-point reparse records and moves the substitute name into `LOG_RECORD.Name`.
- `PrintIrpCode` translates logged major/minor operation codes into display strings, including standard IRPs, FltMgr pseudo-operations, Fast I/O style operations, and transaction notifications.
- `FormatSystemTime` formats local system times as `HH:MM:SS:mmm`.
- `FileDump` writes tab-delimited records with object IDs, flags, operation names, status/information, arguments, and name.
- `ScreenDump` prints a console-oriented one-line record plus optional minor-code continuation line.

Important behavior:
- Uses an aligned 4096-byte receive buffer because kernel records are pointer-aligned and packed back-to-back.
- Detects malformed record lengths before advancing through the returned buffer.
- Polls every 200 ms when no records are available or when the driver reports no more items.
- Exits the process if the kernel component unloads and the port handle becomes invalid.
- Prints memory-pressure markers when record flags indicate out-of-memory or exceeded allocation allowance.

Dependencies and risks:
- Depends on `fltUser.h` messaging, `mspyLog.h` constants, and the exact `LOG_RECORD` layout from `minispy.h`.
- File and screen output duplicate much of the same formatting logic, so operation-code mapping mistakes affect both paths.
- The transaction display switch appears to map `TRANSACTION_NOTIFY_PREPARE_COMPLETE_CODE` to the commit-complete string, which is likely a sample typo.
