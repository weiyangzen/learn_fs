# File Research: sources/windows/winfsp/src/sys/devtimer.c

Imulates Windows `IoInitializeTimer` / `IoStartTimer` / `IoStopTimer` support for platforms where those APIs are unavailable, notably Windows on ARM64.

Global timer:
- `FspDeviceInitializeAllTimers()` initializes a global list, spinlock, DPC, synchronization timer, and starts a 1-second periodic timer.
- `FspDeviceFinalizeAllTimers()` cancels timer, flushes queued DPCs, and in debug asserts the device timer list is empty.

DPC routine:
- `FspDeviceTimerRoutine()` acquires the global timer spinlock and walks all registered `FSP_DEVICE_TIMER` entries, invoking each timer routine with its device object and context.

Per-device timer API:
- `FspDeviceInitializeTimer()` stores callback, device object, and context in the device extension.
- `FspDeviceStartTimer()` inserts the device timer entry into the global list under lock.
- `FspDeviceStopTimer()` removes it under lock.

Important behavior:
- Uses a single global periodic timer for all registered devices.
- Timer callbacks run while the global list spinlock is held, so callbacks must be DPC-safe and avoid operations that could deadlock on the same lock.
