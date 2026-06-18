# sources/storage-engines/foundationdb/flow/include/flow/swift/ABI/Task.h

## Purpose
This Swift ABI header defines the schedulable `swift::Job` layout used by Flow's Swift concurrency hooks. It supplies enough of the Swift runtime task object layout for C++ hook code to inspect and run jobs without including the entire Swift runtime object model.

## Important APIs, Types, and Functions
The header defines `NumWords_HeapObject = 2` and class `swift::Job`, aligned to `2 * alignof(void*)`. `Job` contains fake heap-object storage, `SchedulerPrivate[2]`, `JobFlags Flags`, `uint32_t Id`, `void* Voucher`, and `void* Reserved`. It exposes scheduler-private indexes such as `NextWaitingTaskIndex`, `DispatchLinkageIndex`, and `DispatchQueueIndex`, plus `isAsyncTask()` and `getPriority()`.

## Control Flow
There is no complex control flow. Methods delegate directly to `Flags.isAsyncTask()` and `Flags.getPriority()`. The enum constants compute dispatch-linkage indexes based on pointer and int sizes so layout matches Dispatch expectations on 32-bit and 64-bit targets.

## State and Persistence Behavior
`Job` represents runtime task state owned by Swift. The C++ structure must match the memory layout Swift uses for jobs. Fields are not persisted, but scheduler-private pointers and flags are live runtime coordination state between Swift's runtime, Dispatch, and Flow's network executor hooks.

## Dependencies and Integration Points
The file includes `MetadataValues.h` for `JobFlags` and `JobPriority`. It is consumed by `swift.h` and `swift_concurrency_hooks.h`, especially declarations for hook callbacks and `swift_job_run`.

## Risks
Layout drift is the main risk. Adding, removing, or reordering fields would make Flow call into Swift jobs with incorrect offsets. The fake heap-object storage intentionally avoids pulling in full Swift `HeapObject`; that keeps dependencies small but requires ABI vigilance. Voucher handling is stubbed for non-Darwin platforms.

## Test Signals
Swift interop tests should verify `sizeof(swift::Job)`, alignment, field offsets, and priority extraction against the active Swift runtime. Runtime tests should enqueue jobs through Flow hooks and confirm `swift_job_run` receives a valid job and executor.
