# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/iotimer.c

## Purpose

Implements I/O manager timer support for device objects, wrapping executive timers and dispatching registered per-device timer routines.

## Main State

- `IopTimerLock`
- `IopTimerQueueHead`
- `IopTimerDpc`
- `IopTimer`
- `IopTimerCount`

## Key Functions

- `IopTimerDispatch` runs from the timer DPC, locks the timer list, walks enabled timers, and invokes each timer routine with its device object and context.
- `IopRemoveTimerFromTimerList` removes an I/O timer from the global list and decrements the enabled timer count when needed.
- `IoInitializeTimer` allocates or reuses a device’s `IO_TIMER`, sets routine/context, and inserts it into the global timer queue.
- `IoStartTimer` enables a device timer unless the device extension indicates unload/delete/remove is pending or processed.
- `IoStopTimer` disables an enabled timer and decrements the global count.

## Filesystem Relevance

This is shared I/O infrastructure. Filesystem or storage device objects can register timer callbacks through these APIs for periodic device-level work.

## Dependencies and Coupling

Depends on device object timer fields, device extension lifecycle flags, global I/O timer initialization in `IoInitSystem`, spin locks, DPC timer dispatch, and executive list operations.

## Research Notes

- Timer callbacks are invoked while `IopTimerLock` is held, so callback behavior must be constrained and nonblocking.
- `IoInitializeTimer` inserts into the global timer list each time it is called; callers should avoid repeated initialization patterns that duplicate list entries.
