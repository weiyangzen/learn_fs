## sources/storage-engines/tikv/components/resource_metering/src/recorder/sub_recorder/mod.rs

Purpose: defines the extension contract for resource-specific recorders driven by `Recorder`.

Important APIs/types/functions: the `SubRecorder: Send` trait with hooks `tick`, `collect`, `cleanup`, `pause`, `resume`, and `thread_created`. It exposes `cpu` and `summary` implementations as submodules.

Control flow: `Recorder` invokes these hooks from its timer and task handlers. Most methods default to no-op, letting implementations opt into sampling, batch collection, lifecycle switching, or thread registration.

State/persistence: the trait itself stores no state. It passes mutable access to shared in-memory `RawRecords` and the `HashMap<Pid, LocalStorage>` representing known threads.

Dependencies/integration: depends on `tikv_util::sys::thread::Pid`, `collections::HashMap`, `RawRecords`, and `LocalStorage`. Implementations are boxed in `RecorderBuilder` and run sequentially on the recorder worker thread.

Risks: implementations share mutable `RawRecords`; a slow sub-recorder delays all sampling. Default no-op hooks make missing lifecycle handling easy if a new resource recorder needs enable/disable propagation.

Test signals: behavior is indirectly tested by recorder tests with a mock `SubRecorder`, CPU recorder tests, and summary integration tests.
