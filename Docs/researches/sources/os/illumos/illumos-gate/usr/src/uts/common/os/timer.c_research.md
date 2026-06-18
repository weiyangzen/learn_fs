# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/timer.c

## Purpose

Implements POSIX clock and per-process timer syscalls for illumos. It provides clock backend registration, `clock_gettime` / `clock_settime` / `clock_getres`, POSIX timer creation/deletion/set/get/overrun behavior, signal and event-port notification, timer cleanup on process/LWP lifecycle events, and 32-bit ABI conversions.

## Main Responsibilities

- Maintain a `clock_backend[CLOCK_MAX]` dispatch table.
- Allocate timers from `clock_timer_cache`.
- Enforce `timer_max`, dynamically raised to at least `4 * NCPU`.
- Store timers in each process’s growable `p_itimer` array.
- Lock individual timers using bits in `it_lock` plus `p_lock` and `it_cv`.
- Coordinate deletion with active lockers and backend callbacks.
- Deliver timer expiration by signal queue or event port.
- Support `SIGEV_NONE`, `SIGEV_SIGNAL`, `SIGEV_PORT`, and `SIGEV_THREAD` event forms, with thread notification mapped through event-port style handling.
- Clean up timers when processes exit, LWPs exit, LWPs bind, or associated ports close.

## Key Entry Points

- `clock_timer_init()`
  Creates timer cache and initializes `timer_max`.

- `clock_add_backend()` / `clock_get_backend()`
  Register and retrieve clock backends.

- `clock_settime()`
  Checks backend validity and `secpolicy_settime()`, copies in native or 32-bit timespec, validates it, and calls backend `clk_clock_settime()`.

- `clock_gettime()`
  Calls backend `clk_clock_gettime()` and copies out native or 32-bit timespec, checking 32-bit overflow.

- `clock_getres()`
  Handles POSIX NULL-`tp` no-op semantics, calls backend resolution function, and copies out native or 32-bit result.

- `timer_create()`
  Validates clock/backend and notification event, allocates sigqueue and `itimer_t`, finds or grows a per-process timer slot, initializes signal/port metadata, associates event-port resources when requested, calls backend `clk_timer_create()`, copies out timer ID, and releases the new timer.

- `timer_gettime()`
  Grabs the timer, calls backend `clk_timer_gettime()`, releases it, and copies out native or 32-bit interval spec.

- `timer_settime()`
  Optionally returns old time, copies in and validates new interval/value, grabs timer, calls backend `clk_timer_settime()`, and releases it.

- `timer_delete()`
  Grabs and deletes a timer.

- `timer_getoverrun()`
  Returns the last overrun value under `p_lock`.

- `timer_lwpexit()`
  Clears `it_lwp` for timers created by the exiting LWP.

- `timer_lwpbind()`
  Notifies backends when the creating LWP’s CPU binding changes.

- `timer_exit()`
  Deletes all timers for the current process and frees the process timer array.

## Internal Helpers

- `timer_lock()` / `timer_unlock()`
  Serialize access to an individual timer while holding `p_lock`.

- `timer_delete_locked()`
  Marks a timer for removal, waits for blockers to observe removal, clears the process timer slot, calls backend deletion, dissociates/free event-port resources, handles pending sigqueue lifetime, and frees the timer.

- `timer_grab()` / `timer_release()` / `timer_delete_grabbed()`
  Public-syscall-friendly wrappers around timer lookup and locking.

- `timer_get_id()`
  Finds an unused timer ID and grows `p_itimer` by doubling up to `timer_max`, handling races while `p_lock` is dropped for allocation.

- `timer_fire()`
  Backend callback for expirations. It increments pending/overrun state, sends event-port notifications, or queues timer signals with `sigaddqa()`.

- `timer_signal()`
  Signal-queue completion callback that transfers pending count to `it_overrun` and clears pending state.

- `timer_port_callback()`
  Event-port delivery callback that reports pending count as event count and resets the timer pending counter.

- `timer_close_port()`
  Scans current process timers and detaches/free event-port resources for the closing port.

## Locking and Lifetime Model

- `p_lock` protects process timer slot lookup, timer lock bits, deletion state, and signal timer overrun access.
- `it_mutex` protects `it_pending`, port event resources, and races between `timer_fire()` and `timer_signal()`.
- Deletion sets `ITLK_REMOVE` before removing the process slot, ensuring new `timer_grab()` calls fail.
- Backend `clk_timer_delete()` must guarantee `timer_fire()` has completed and will not be called again for that timer.
- Pending signal queue memory is freed immediately only when no pending signal references it; otherwise `sq_func` is set to `NULL` for synchronous freeing later in `siginfofree()`.

## Filesystem Relevance

This is timer/syscall infrastructure rather than filesystem logic. It still matters to filesystem behavior because timed waits, signal interruption, event ports, asynchronous daemons, and timeout-driven kernel/user workflows depend on accurate clock and timer delivery. Filesystem services using event ports or signal-driven control paths rely on this substrate.

## Notable Edge Cases

- `clock_getres(clock, NULL)` returns success without validating the clock ID, matching POSIX behavior noted in the source.
- `timer_create()` uses short `oldsigevent` copyin for binary compatibility.
- 32-bit callers get explicit timespec/itimerspec conversion and overflow checks.
- `SIGEV_THREAD` and `SIGEV_PORT` both allocate event-port resources.
- Timer IDs are array indexes and may skip newly freed lower slots after a racing resize.
- If a timer’s creating LWP exits, behavior is documented as undefined to users; illumos clears `it_lwp` and leaves backend state otherwise intact.
- `timer_close_port()` iterates up to `timer_max` using `timer_grab()`, so sparse timer arrays are handled by failed grabs.
