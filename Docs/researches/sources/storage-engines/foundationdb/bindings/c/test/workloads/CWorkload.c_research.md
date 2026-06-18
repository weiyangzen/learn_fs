## sources/storage-engines/foundationdb/bindings/c/test/workloads/CWorkload.c

Purpose: sample external C workload implementation for the simulation workload ABI declared by `foundationdb/CWorkload.h`. It demonstrates how a C shared library exports a factory and implements setup/start/check/metrics/timeout/free callbacks.

Important APIs and types: `CWorkload` stores workload name, client id, and `FDBWorkloadContext`. `DelayParameter` keeps asynchronous delay callback state. The `WITH` macro calls function pointers in context, promise, string, and metric vtables. `workloadCFactory` is the exported entry point returning `FDBWorkload` with `FDB_WORKLOAD_API_VERSION` and `CWorkload_vt`.

Control flow: the factory copies the borrowed workload name, reads client metadata, logs options twice to show option consumption semantics, allocates `CWorkload`, and returns the vtable. `setup` and `check` trace and immediately resolve promises. `start` schedules a context delay whose callback logs elapsed time, sends the promise, frees the promise, and frees callback parameters. `getMetrics` reserves and pushes a `test=42` metric.

State and persistence: no database state is touched despite receiving `FDBDatabase*`. Runtime state is heap allocated per workload and callback. Promise ownership is explicitly released by `send` and `free`.

Dependencies and integration points: bridges dynamic C workloads into FoundationDB simulation, requiring `fdb_future_set_callback` and the workload context vtable. It is built as a shared object such as `libc_workload.so`.

Risks: manual memory management is central. Misordered promise free/send or failing to free copied strings would leak or double-free. The delay callback casts callback types across C declarations, so ABI drift in `CWorkload.h` is high risk.

Test signals: validates C workload lifecycle, tracing, option retrieval, asynchronous delay, metrics, and timeout plumbing.
