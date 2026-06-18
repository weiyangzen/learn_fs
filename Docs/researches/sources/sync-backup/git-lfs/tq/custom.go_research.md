# sources/sync-backup/git-lfs/tq/custom.go

Purpose: custom transfer adapter implementation for external line-oriented JSON transfer processes, including standalone file agent support.

Important APIs/types/functions: `customAdapter`, `traceWriter`, worker context, init/transfer/terminate request structs, response struct, constructors, `Begin`, `WorkerStarting`, message exchange helpers, shutdown/abort, `DoTransfer`, `newCustomAdapter`, `configureDefaultCustomAdapters`, `configureCustomAdapters`, and `customAdapterConfig`.

Control flow: `Begin` limits concurrency when adapter config says non-concurrent. Each worker starts an external command, wires stdin/stdout/stderr, sends `init`, and then each transfer sends upload/download JSON and reads progress or complete messages until done. Download completions verify hash and move file; upload completions run verify. Worker shutdown sends terminate and waits up to 30 seconds before killing.

State and persistence: owns subprocesses, pipes, buffered readers, trace buffers, and optional downloaded temp paths returned by the custom adapter.

Dependencies and integration points: custom adapters are registered from Git config keys `lfs.customtransfer.<name>.*`; manifest may use them as standalone transfer agents. Depends on `subprocess`, `tools.VerifyFileHash`, and `RenameFileCopyPermissions`.

Risks: protocol is strict: unexpected OIDs/events fail transfers. External process hangs are bounded only during shutdown, not during normal response reads. Stderr is logged to tracer; sensitive output could leak in trace. Shell formatting/path args require careful quoting.

Test signals: `custom_test.go` covers config registration, direction filtering, args, and concurrency flags, but not subprocess protocol execution.
