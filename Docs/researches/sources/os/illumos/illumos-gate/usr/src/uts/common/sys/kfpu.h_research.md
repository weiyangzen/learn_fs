# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kfpu.h

## Role

`kfpu.h` defines the kernel API for opting into floating-point unit use. It gives kernel code a controlled way to allocate FPU state and bracket FPU usage so state can be saved/restored across context switches.

## Major Definitions

`kfpu_state_t` is an opaque kernel FPU state object. Flags for begin/end are `KFPU_NO_STATE`, meaning no explicit `kfpu_state_t` is passed and preemption-based handling is used, and `KFPU_USE_LWP`, meaning no explicit state is passed and LWP state is used.

## Interfaces

`kernel_fpu_alloc()` and `kernel_fpu_free()` manage reusable FPU state. `kernel_fpu_begin()` and `kernel_fpu_end()` bracket a thread's FPU-using region. `kernel_fpu_no_swtch()` is an internal validation hook.

## Integration Notes

The file warns that FPU use in the kernel requires care. A `kfpu_state_t` may be allocated independently from use and is not permanently thread-bound, but only one thread may use a given state object at a time. Missing or mismatched begin/end calls risk corrupting user or kernel FPU state.
