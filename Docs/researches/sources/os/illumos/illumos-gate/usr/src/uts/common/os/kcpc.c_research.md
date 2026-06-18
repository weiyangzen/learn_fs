# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/kcpc.c

## Role

`kcpc.c` implements the kernel CPU performance counter framework. It binds performance counter request sets to LWPs or CPUs, configures platform counter backends, handles context switching, overflow interrupts, DTrace CPC integration, CPU capacity/utilization interposition, and request multiplexing.

## Backend And Initialization

`kcpc_init()` initializes global locks once and loads the platform PCBE module through `kcpc_hw_load_pcbe()`. `kcpc_register_pcbe()` installs the backend operations and counter count. PCBE callbacks perform event coverage, configuration, programming, sampling, stopping, freeing, and event/attribute listing.

`kcpc_pcbe_tryload()` loads qualified PCBE modules by platform-specific ID components.

## Binding And Configuration

`kcpc_bind_thread()` creates a frozen context for an LWP, assigns requests to hardware counters, configures PCBE request state, installs context ops, and programs the hardware if binding the current thread. It supports `CPC_BIND_LWP_INHERIT`.

`kcpc_bind_cpu()` creates a CPU-bound context, requires the current thread to be bound to the requested CPU, rejects conflicting non-CU CPC use, and programs the target CPU while holding CPU and CPC context locks.

`kcpc_assign_reqs()` and `kcpc_tryassign()` place requests onto counters, preserving explicit assignments and trying different starting requests to avoid simple ordering failures.

`kcpc_configure_reqs()` calls `pcbe_configure()` for each request, sets overflow-notification state, links request data storage, and maps PCBE errors to kernel errno values.

## Sampling, Enablement, And Teardown

`kcpc_sample()` validates the set, samples current hardware when appropriate, updates hrtime and virtual tick accounting, and copies counter data, time, and tick values to user buffers.

`kcpc_enable()` supports enable/disable and user/system counting flag changes. For user/system mode toggles it stops, snapshots presets, duplicates the set, unbinds, edits flags, and rebinds.

`kcpc_unbind()`, `kcpc_passivate()`, and `kcpc_free()` invalidate contexts, stop hardware when needed, remove context ops, clear thread state, free PCBE configs, release set data, and coordinate with concurrent `kcpc_restore()` using `KCPC_CTX_RESTORE`.

## Context Switching And Overflow

`kcpc_save()` stops counters on switch-out, samples active thread-bound contexts, and may restore CU counter use. `kcpc_restore()` avoids invalid/frozen contexts, marks restore-in-progress, and programs the hardware at high PIL with preemption disabled.

`kcpc_hw_overflow_intr()` handles hardware overflow interrupts. If DTrace CPC is active, it coordinates per-CPU interrupt state, fires DTrace, resets overflowed counters, and reprograms. Otherwise it calls `kcpc_overflow_intr()` to either post an AST for LWP-bound overflow handling or synchronously sample/restart a CPU-bound context.

`kcpc_overflow_ast()` samples after an overflow, detects PICs marked for `CPC_OVF_NOTIFY_EMT`, preserves freeze state for signal delivery, or restarts counters.

## CPU And CU Integration

`kcpc_program()` and `kcpc_unprogram()` are high-PIL routines used locally or via cross-call. They interpose with capacity/utilization CPC use through `cu_cpc_unprogram()` and `cu_cpc_program()`.

`kcpc_cpu_ctx_create()` creates one or more CPU contexts from a request list, splitting or degrading to one request per set when counters cannot cover all events simultaneously.

`kcpc_cpu_stop()` and `kcpc_cpu_program()` use `cpu_call()` wrappers to stop or program counters on remote CPUs.

## Research Notes

This file has substantial concurrency and interrupt-context risk. Important invariants include preemption disabled while programming/sampling hardware, high-PIL synchronization with cross-calls, `cpu_lock` while dereferencing CPU structures, set binding completion signaled by `KCPC_SET_BOUND`, and atomic flag updates. Audit hotspots are overflow skid handling, invalidation races, PCBE config lifetime, CPU DR/offline paths, inherited LWP contexts, and CU interposition.
