# sources/storage-engines/tikv/components/panic_hook/src/lib.rs

## Purpose
`panic_hook` is a test-only helper that temporarily mutes panic output and catches unwinds. It keeps tests that intentionally panic from emitting noisy stack traces.

## Important APIs, Types, and Functions
- `mute` installs the custom hook once and marks the current thread as muted.
- `unmute` clears the current thread's muted flag.
- `recover_safe` mutes, runs a closure inside `catch_unwind(AssertUnwindSafe)`, unmutes, and returns the panic result.
- `track_hook` delegates to the original default hook unless the thread-local muted flag is true.

## Control Flow
`initialize` stores the original hook in a leaked raw pointer and installs `track_hook` through `Once`. Muting is thread-local, so only the calling thread suppresses output. `recover_safe` always calls `unmute` after `catch_unwind` returns.

## State and Persistence Behavior
State is global hook installation plus thread-local `MUTED`. The original hook pointer is stored for process lifetime and is not restored. No persistent storage is used.

## Dependencies and Integration Points
Used by tests such as `keys::test_data_key` to verify assertions without noisy panic logs. It depends only on `std::panic`, `Once`, and thread-local storage.

## Risks
The global hook uses `static mut` and raw pointer storage. Although installation is protected by `Once`, this design assumes the original hook remains valid forever. If a closure aborts the process or uses non-unwind panics, `recover_safe` cannot recover. `AssertUnwindSafe` shifts unwind-safety responsibility to the caller.

## Test Signals
No local tests are present; dev-dependency use in other crates validates behavior.
