# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/passThrough/passThrough.c

Pass-through minifilter sample that registers broad pre/post callbacks without changing I/O.

Key responsibilities:
- Registers callbacks for most standard IRP operations, FSFilter callbacks, Fast I/O-style operations, network query open, MDL operations, and volume mount/dismount.
- Uses `PtPreOperationPassThrough` and `PtPostOperationPassThrough` for normal pass-through operations.
- Uses `PtPreOperationNoPostOperationPassThrough` for shutdown, where post callbacks are unsupported.
- Registers instance setup, query teardown, teardown start, teardown complete, and unload routines.
- Optionally requests operation-status callbacks for oplock and directory-change notification operations.

Important behavior:
- `DriverEntry` registers the filter and starts filtering; failure after registration unregisters the filter.
- Instance setup and detach query always return success.
- Pre-operation callback returns `FLT_PREOP_SUCCESS_WITH_CALLBACK` for registered post operations.
- Post-operation callback simply returns `FLT_POSTOP_FINISHED_PROCESSING`.
- `PtDoRequestOperationStatus` requests status callbacks for oplock FSCTLs and `IRP_MN_NOTIFY_CHANGE_DIRECTORY`.

Dependencies and risks:
- Depends on `fltKernel.h` and FltMgr callback semantics.
- `gTraceFlags` defaults to zero, so debug tracing is silent unless changed.
- `OperationStatusCtx` is incremented without synchronization; it is only diagnostic context in this sample.
- The file is useful as a callback-coverage template, not as a policy filter.
