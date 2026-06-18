# sources/user-network-fs/rclone/librclone/librclone/librclone.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/librclone/librclone.go -->
## sources/user-network-fs/rclone/librclone/librclone/librclone.go

Purpose: internal implementation shared by C and gomobile librclone bindings, translating JSON strings to rclone RC calls and JSON responses.

Important APIs and control flow: `Initialize` starts logging, installs config-file handling, and starts accounting using a background context. `Finalize` currently forces a GC and has TODOs for deeper cleanup. `RPC(method, input)` creates an `rc.Params`, recovers panics into JSON errors, decodes input JSON when non-empty, finds the registered RC call, rejects calls needing raw request or response, runs the call as a `jobs.NewJob`, defaults nil output to an empty params map, and serializes output with `rc.WriteJSON`. `writeError` logs, builds `rc.Error` params, and falls back to hand-written JSON if serialization fails.

State, dependencies, and integration: depends on rclone config, accounting, logging, RC registry, RC jobs, and standard JSON/http/runtime packages. It has process-wide initialization side effects but stores no explicit initialized flag.

Risks and test signals: unsupported request/response RC methods return 404. `Finalize` does not cancel async jobs or close all global services. Input must be a JSON object. Panic recovery returns stack traces in JSON errors. C and Python tests cover `rc/noop` and `rc/error`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/librclone/librclone.go -->
