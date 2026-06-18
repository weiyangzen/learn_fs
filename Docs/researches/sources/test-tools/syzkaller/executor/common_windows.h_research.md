# sources/test-tools/syzkaller/executor/common_windows.h

Purpose: Windows implementation of executor/csource common primitives for exception-safe memory access, timing, threading, events, sandbox-none execution, and temporary directories.

Important APIs and control flow: `install_segv_handler` is a no-op because Windows structured exception handling is used directly. `NONFAILING` wraps arbitrary statements in `__try/__except` and returns false on access faults. `current_time_ms` and `sleep_ms` map to `GetTickCount64` and `Sleep`. `thread_start` creates a 128 KiB-stack Windows thread. `event_t` combines `CRITICAL_SECTION`, `CONDITION_VARIABLE`, and integer state; `event_set` rejects double-set events, `event_wait` blocks until state is set, and `event_timedwait` waits until timeout. `do_sandbox_none` calls the external `loop`. `use_temporary_dir` creates and enters a `./syzkaller.XXXXXX` temp directory using `mktemp`, `CreateDirectory`, and `_chdir`.

State and dependencies: event state is process-local and manually synchronized. The header depends on `windows.h`, `io.h`, `_chdir`, and executor helpers `exitf`.

Integration points: included through Windows common/executor builds and shared with generated C reproducers under feature macros.

Risks and tests: `event_reset` writes `state` without taking the critical section, so callers must preserve the executor's event ordering assumptions. `mktemp` is weaker than atomic temp creation. Coverage is not implemented here; Windows executor-specific syscall execution and read/write shims are in `executor_windows.h`. Test signals are mostly compile/build coverage for the Windows target.
