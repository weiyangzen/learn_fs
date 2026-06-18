<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClRecorder.hh -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClRecorder.hh

Purpose: implements the XrdCl recorder file plugin. It wraps `XrdCl::File`, records supported file operations and their asynchronous responses, and writes CSV rows for replay and analysis.

Important APIs/types/functions: nested singleton `Output` owns the CSV fd and serialized writes; `Output::Instance()` opens the output lazily; `Output::Write()` writes a complete action row under lock; `Recorder::RecordHandler` wraps user response handlers and records callback results; `Recorder::SetOutput()` selects `XRD_RECORDERPATH`, config path, or `/tmp/xrdrecord.csv`; operation overrides create the matching `Action` subclass and submit the wrapped call with a `RecordHandler`.

Control flow: factory code calls `SetOutput()`, construction binds `output` to `Output::Instance()`, and each intercepted async operation allocates an `Action` plus self-deleting `RecordHandler`. When XrdCl completes the request, the handler records status/response, writes CSV, forwards the callback to the original handler when present, and deletes itself.

State/persistence: persistent output is the CSV file. It is opened with `O_CREAT|O_WRONLY|O_TRUNC`, so first open truncates prior content. `Output` is a process singleton shared by all recorder instances and protected by a mutex. Each `Recorder` owns one `XrdCl::File`.

Dependencies/integration: depends on `XrdCl::FilePlugIn`, `XrdCl::File`, `ResponseHandler`, `DefaultEnv` logging, POSIX `open/write/close`, and action classes from `XrdClAction.hh`.

Risks/test signals: `Output::IsValid()` checks `fd > 0`, so a valid fd `0` would be treated invalid, though normal opens usually produce fd 3+. If `file.Open()` or another operation returns immediate failure without invoking the response handler, the allocated `RecordHandler` may leak and no action row is written. Visa and property operations are not recorded. Tests should cover output path precedence, failed output open, concurrent operations writing complete rows, immediate submission failures, null user handlers, and each recorded operation's callback forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClRecorder.hh -->
