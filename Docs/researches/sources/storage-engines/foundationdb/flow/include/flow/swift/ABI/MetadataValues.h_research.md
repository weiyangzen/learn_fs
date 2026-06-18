# sources/storage-engines/foundationdb/flow/include/flow/swift/ABI/MetadataValues.h

## Purpose
This vendored Swift ABI header defines target-independent metadata constants and flag wrappers needed by Flow's embedded Swift concurrency interop. It mirrors selected Swift runtime/compiler ABI structures without pulling in the full Swift runtime headers.

## Important APIs, Types, and Functions
It defines ABI size constants such as `NumWords_ValueBuffer`, `NumWords_AsyncTask`, `NumWords_TaskGroup`, and `NumBytes_UniqueHash`; forward declarations for `InProcess`, `TargetMetadata`, and `Metadata`; enums `JobKind`, `JobPriority`, `TaskOptionRecordKind`, and `ContinuationStatus`; helper `descendingPriorityOrder`; and flag wrapper classes `JobFlags` and `AccessibleFunctionFlags`. `JobFlags` exposes fields for job kind and priority plus task-specific flags such as child task, future, group child, and async-let task.

## Control Flow
The header has minimal runtime control flow. `descendingPriorityOrder` returns `0`, `-1`, or `1` to order higher priority values first. `JobFlags` operations are inherited from `FlagSet`: constructors set kind and priority, accessors read/write packed fields, and flag accessors manipulate individual bits.

## State and Persistence Behavior
No state is persisted. The important "state" is bit-level ABI layout: `JobFlags` uses a `uint32_t` with kind in bits 0-7, priority in bits 8-15, and task flags in bits 24-28. These values must stay aligned with the Swift runtime ABI expected by compiled Swift code.

## Dependencies and Integration Points
It depends on `flow/swift/Basic/FlagSet.h` plus standard integer headers. `flow/swift/ABI/Task.h` consumes `JobFlags`, `JobPriority`, and `JobKind`. Flow's Swift concurrency hooks inspect `swift::Job` priority/kind through these definitions.

## Risks
Any drift from the Swift ABI version used by the compiler/runtime can corrupt job scheduling behavior. The flag macros rely on valid field widths and values; debug `assert` catches out-of-range fields only when assertions are enabled. `JobPriority` numeric values are copied from Dispatch QoS and must be mapped carefully to Flow priorities.

## Test Signals
Swift-enabled ABI tests should validate `sizeof`, alignment, and field offsets against the Swift runtime version in use. Unit tests for `JobFlags` should verify opaque bit patterns for kind, priority, and task flags. Scheduling tests should confirm priority ordering and Flow priority conversion.
