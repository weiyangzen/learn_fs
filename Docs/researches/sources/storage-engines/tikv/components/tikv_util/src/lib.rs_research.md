# sources/storage-engines/tikv/components/tikv_util/src/lib.rs

## Purpose
Defines the root `tikv_util` crate surface, re-exporting utility modules and implementing shared process, panic, collection, byte-escaping, readiness, and small generic helper APIs used across TiKV.

## Important APIs, Types, And Functions
The crate enables nightly features used by submodules and exposes modules such as `config`, `future`, `deadline`, `logger`, `lru`, `math`, `sys`, `timer`, and `worker`. Global flags include `PANIC_WHEN_UNEXPECTED_KEY_OR_DATA`, `PANIC_MARK`, and `GLOBAL_SERVER_READINESS`.

Core helpers include panic mark file functions, marker traits (`AssertClone`, `AssertCopy`, `AssertSend`, `AssertSync`), `slices_in_range`, `HandyRwLock`, `escape`, `unescape`, `TryInsertWith::or_try_insert_with`, `get_tag_from_thread_name`, `DeferContext`, `Either`, `RingQueue`, `is_even`, `MustConsumeVec`, panic-context storage and `set_panic_context!`, `set_panic_hook`, `check_environment_variables`, `run_and_wait_child_process`, `is_zero_duration`, `empty_shared_slice`, `build_on_master_branch`, `set_vec_capacity`, and `ServerReadiness`.

## Control Flow
Panic flag helpers wrap atomics with sequential consistency. `escape` converts bytes to printable ASCII with protobuf-style octal escapes; `unescape` reverses supported escape forms and panics on malformed input. `TryInsertWith` runs a fallible initializer only for vacant hash-map entries. `DeferContext` executes its closure on drop.

`RingQueue::push` drops the oldest item when capacity is full. `MustConsumeVec` dereferences as a vector but panics safely on drop if non-empty, making resource leaks visible without double-panicking during unwind. Panic context is thread-local; `set_panic_context!` prefixes keys with file/line and returns a guard that removes them on drop.

`set_panic_hook` warms backtrace metadata in a background thread, logs panic message/thread/location/backtrace/context, swaps async logging to a synchronous terminal logger for flush safety, optionally creates a panic mark file, and then aborts or calls `libc::_exit(1)`. `check_environment_variables` ensures `TZ` is set on Unix and logs selected networking/proxy variables. `run_and_wait_child_process` forks, runs a closure in the child, and returns the parent's observed exit status. `ServerReadiness::is_ready` requires both PD connectivity and raft peer catch-up flags.

## State And Persistence
Persistent effects include creating `panic_mark_file` in a data directory and environment mutation for missing `TZ`. Most other state is process-local: atomics, thread-local panic context, ring buffers, readiness atomics, and logger replacement during panic handling.

## Dependencies And Integration
Depends on many standard utilities plus `nix` fork/wait, `lazy_static`, `serde`, `backtrace`, TiKV logger/thread wrappers, and exported macros. It is the integration hub used by nearly all TiKV components importing `tikv_util`.

## Risks
`unescape` intentionally panics for malformed input and assumes trusted/validated strings. `set_panic_hook` runs in crash context, so logging, backtrace generation, and file creation must remain best-effort and avoid relying on full runtime health. `run_and_wait_child_process` is Unix/fork oriented and should not be used in multi-thread-sensitive paths outside tests. `set_vec_capacity` uses `reserve_exact(cap - len)` when growing toward capacity, so callers should pass a capacity at least as large as the current length.

## Test Signals
Tests cover panic hook behavior in a child process, panic mark path/existence, ring queue eviction/removal, defer execution, RwLock guard behavior, VecDeque slicing across wrap points, must-consume leak detection and double-panic prevention, unescape forms, zero-duration checks, and scoped panic-context cleanup.
