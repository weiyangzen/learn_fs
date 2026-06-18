# sources/storage-engines/foundationdb/flow/include/flow/swift_concurrency_hooks.h

## Purpose
This header exposes the C/C++ declarations and inline installers that let Flow take over Swift global executor enqueueing. It bridges Swift runtime hook variables to Net2 or simulator scheduling so Swift async jobs can be run on Flow's event loop.

## Important APIs, Types, and Functions
The file defines Swift compiler/visibility/calling-convention macros such as `SWIFT_READONLY`, `SWIFT_RUNTIME_EXPORT`, `SWIFT_EXPORT_FROM`, `SWIFT_CC(swift)`, `SWIFT_CONTEXT`, and related attributes. It declares Swift runtime hook function-pointer variables: `swift_task_enqueueGlobal_hook`, `swift_task_enqueueGlobalWithDelay_hook`, `swift_task_enqueueGlobalWithDeadline_hook`, and `swift_task_enqueueMainExecutor_hook`, plus `swift_job_run`. Flow-specific hook implementations are declared as `net2_enqueueGlobal_hook_impl` and `sim2_enqueueGlobal_hook_impl`. Inline helpers are `installSwiftConcurrencyHooks`, `newNet2ThenInstallSwiftConcurrencyHooks`, and `globalNetworkRun`.

## Control Flow
Preprocessor flow selects attributes for Mach-O/WASI, ELF, Cygwin, or PE/COFF and checks which Swift libraries are being exported. At runtime, `installSwiftConcurrencyHooks` assigns Swift's global enqueue hook to simulator or Net2 implementation when `WITH_SWIFT` is enabled; otherwise it asserts. `newNet2ThenInstallSwiftConcurrencyHooks` creates `TLSConfig`, initializes `g_network` through `_swift_newNet2`, and installs Net2 hooks. `globalNetworkRun` blocks in `g_network->run()`.

## State and Persistence Behavior
The header mutates process-global Swift runtime hook variables and Flow's global `g_network` pointer. There is no persisted data. Hook installation is process-wide and should be treated as singleton runtime state; installing the wrong hook changes how every Swift async task in the process is scheduled.

## Dependencies and Integration Points
It depends on `swift.h`, `swift/ABI/Task.h`, `flow/AsioReactor.h`, and `flow/TLSConfig.h`. It must match Swift runtime exported symbol names and calling conventions. It integrates Flow's Net2 reactor, simulator scheduling, and Swift `swift_job_run` with an `ExecutorRef`.

## Risks
ABI/calling-convention mismatch can crash immediately because hook functions use Swift calling conventions. Visibility macros must be right for each platform or runtime hook symbols may fail to link. Hook globals are nullable/non-null annotated but not protected by synchronization here. `newNet2ThenInstallSwiftConcurrencyHooks` allocates `TLSConfig` and initializes global network state inline, so repeated calls or calls after another network is installed are risky. Non-Swift builds assert if installation is attempted.

## Test Signals
Swift-enabled integration tests should install hooks in simulator and Net2 modes, enqueue immediate, delayed, deadline, and main-executor jobs, and verify they run on the Flow network. Link tests should cover ELF, Mach-O, and Windows visibility branches. Non-Swift builds should compile and assert on accidental installation attempts.
