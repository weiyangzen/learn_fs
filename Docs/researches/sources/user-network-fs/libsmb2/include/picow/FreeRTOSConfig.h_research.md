# sources/user-network-fs/libsmb2/include/picow/FreeRTOSConfig.h

## Purpose
`FreeRTOSConfig.h` configures the FreeRTOS kernel for Pico W libsmb2 examples or builds.

## Important APIs, Types, and Functions
It enables preemption, mutexes, recursive mutexes, counting semaphores, queue sets, software timers, dynamic allocation, trace facility, and common task APIs. It sets a 1 kHz tick rate, 32 priorities, 2048 minimal stack units, 128 KiB heap, and `configASSERT(x)` to `assert(x)`. SMP-specific macros are enabled when `FREE_RTOS_KERNEL_SMP` is set.

## Control Flow
No libsmb2 control flow exists here. FreeRTOS uses the macros at compile time to include/exclude scheduler, timer, allocation, and task APIs.

## State and Persistence Behavior
Runtime state is FreeRTOS-managed heap, tasks, queues, semaphores, and timers sized according to this header. No filesystem persistence occurs.

## Dependencies and Integration Points
It integrates with Pico SDK/FreeRTOS and lwIP socket support used by libsmb2 on Pico W. `configENABLE_BACKWARD_COMPATIBILITY` is explicitly enabled for lwIP `sys_arch` compilation.

## Risks and Edge Cases
The 128 KiB heap and 1024 timer/thread stack sizes can be tight for SMB sessions with signing/encryption buffers. `configUSE_NEWLIB_REENTRANT` is disabled, which can matter for libc calls in multi-tasking examples. Stack overflow and malloc failed hooks are disabled.

## Test Signals
Build Pico W examples, run concurrent SMB operations under FreeRTOS, monitor heap and stack high-water marks, and test lwIP integration in both SMP and non-SMP configurations.
