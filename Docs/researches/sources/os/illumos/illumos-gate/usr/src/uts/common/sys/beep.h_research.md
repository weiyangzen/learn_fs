# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/beep.h

This kernel-only header defines the abstract system beeper API and state structures. It separates generic beeper scheduling/queuing from hardware-specific on/off/frequency callbacks.

Key contents:
- `beep_entry_t`: queued frequency/duration pair.
- Callback types:
  - `beep_on_func_t`
  - `beep_off_func_t`
  - `beep_freq_func_t`
- `beep_state_t`: callback private arg, mode enum, callback pointers, timeout id, mutex, circular queue indices/size, and queue pointer.
- `BEEP_QUEUE_SIZE`.
- Beep type enum: `BEEP_DEFAULT`, `BEEP_CONSOLE`, `BEEP_TYPE4`.
- `beep_params_t` with type, frequency, and duration.
- Kernel API prototypes for init/fini, on/off/frequency control, default beep, polled beep, tone creation, timeout handler, and busy check.

Dependencies:
- Includes `sys/mutex.h`.
- Almost all contents are under `_KERNEL`.
- C++ guarded with `extern "C"`.

Research notes:
- This is not a user-facing sound API; it is a kernel abstraction for console/system tones.
- Queue state is protected by `beep_state_t.mutex`.
