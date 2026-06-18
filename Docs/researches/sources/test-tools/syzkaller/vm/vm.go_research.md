# sources/test-tools/syzkaller/vm/vm.go

Purpose: high-level VM abstraction used by syzkaller managers and tools. It wraps `vmimpl` backends with pool creation, per-instance workdirs, snapshot helpers, command execution monitoring, crash report extraction, diagnostics, output trimming, shutdown handling, and dispatcher integration.

Important APIs/types/functions: `Pool`, `Instance`, `ShutdownCtx`, `vmType`, `AllowsOvercommit`, `Create`, `Pool.Create`, `Pool.Close`, `SetupSnapshot`, `RunSnapshot`, `Copy`, `Forward`, `RunOptions`, `WithExitCondition`, `WithBeforeContext`, `WithInjectExecuting`, `WithEarlyFinishCb`, `Instance.Run`, `RunStream`, `Info`, `Close`, `NewDispatcher`, and the internal `monitor`.

Control flow: `Create` resolves the registered backend type, builds `vmimpl.Env`, invokes its constructor, applies debug count limiting, and records timeout/stat configuration. `Pool.Create` makes a process temp workdir, optionally copies a template, asks the backend to create an instance, and increments active count. `Instance.Run` calls backend `Run`, then `monitorExecution` multiplexes VM chunks, command errors, timeouts, injected execution heartbeats, and global shutdown. It converts normal/error/timeout/no-output outcomes into parsed reports or synthetic reports, calls backend diagnostics when needed, waits briefly for delayed output, and trims reports to configured context.

State and persistence: each instance owns a temp workdir removed on `Close`; pool state tracks active instance count and output byte stats. Snapshot state is a boolean guard enforcing `SetupSnapshot` before `RunSnapshot`.

Dependencies and integration: imports all backend packages for registration, plus manager config, target timeouts, report parsing, crash types, stats, dispatcher, and `vmimpl`. It is the main integration point between VM backends and syzkaller execution/reporting code.

Risks: `Pool.Close` panics if instances remain active; monitor assumes `extractErrors` is called once; `NoOutput` depends on either console output or explicit execution markers; report trimming can drop far-back context; default synthetic errors may race with late kernel crashes; global `Shutdown` is process-wide.

Test signals: `vm_test.go` covers monitor exit conditions, diagnostics, preemption, no-output detection, delayed crashes, output trimming, nil output channels, VM type parsing, and multiple-error extraction. `vm_full_test.go` covers repeated real command runs through `Multiplex`.
