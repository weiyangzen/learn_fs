# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwFob.cc

Purpose: implements destructor-time diagnostics for the per-file pgwrite checksum-tracking object.

Important APIs/types/functions: `XrdXrootdPgwFob::~XrdXrootdPgwFob()` logs warnings and optional trace details about outstanding checksum errors, fixed counts, and remaining bad extents.

Control flow: on destruction, it counts uncorrected bad offsets. If any remain, it logs a warning with the file key. When page-checksum tracing is enabled, it formats each bad extent as length/page-index and emits either a detailed remaining-area trace or a summary trace when all errors were fixed.

State and persistence behavior: reads `badOffs`, `numErrs`, `numFixd`, and `fileP`. The destructor itself does not persist repairs; it emits log/trace diagnostics at file-object teardown.

Dependencies: `XrdOucString`, `XrdSysError`, `XrdXrootdFile`, `XrdXrootdPgwFob`, `XrdXrootdTrace`, protocol page-size constants, and global `XrdXrootd::eLog`.

Integration points: file objects owning `pgwFob` get final diagnostics when closed/destroyed after pgwrite checksum activity. `XrdXrootdPgwBadCS::boAdd()` populates this object.

Risks: destructor assumes `fileP` and `fileP->FileKey` are still valid. Diagnostic formatting can become large for many bad offsets but is gated by trace for detailed output. Warnings on outstanding errors are operationally important and should not be suppressed accidentally.

Test signals: destruction with no errors, fixed errors only, outstanding errors, trace enabled/disabled, offset length encoding for full and partial pages, and file key lifetime during teardown.
