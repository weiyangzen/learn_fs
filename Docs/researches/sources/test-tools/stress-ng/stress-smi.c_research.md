# sources/test-tools/stress-ng/stress-smi.c

## Purpose

`stress-smi.c` implements the `smi` stressor, which triggers x86 System Management Interrupts by writing a no-op command to the APM I/O port. It optionally reads the x86 `MSR_SMI_COUNT` model-specific register before and after the run to estimate SMI rate. On x86_64 it also checks that SMI handling does not unexpectedly clobber general-purpose registers other than the registers used by the `out` instruction.

## Important APIs, Types, and Functions

- `MSR_SMI_COUNT`, `APM_PORT`, and `STRESS_SMI_NOP` define the hardware interfaces used by the stressor.
- `smi_regs_t`, `SAVE_REG`, and `SAVE_REGS` capture x86_64 register snapshots around the port write.
- `stress_smi_supported()` enforces `CAP_SYS_MODULE`, `CAP_SYS_RAWIO`, root privileges, and CPU MSR support before the stressor is allowed to run.
- `stress_smi_count()` sums `MSR_SMI_COUNT` across all online CPUs via `stress_x86_readmsr64()`.
- `stress_smi()` is the entry point. It tries to load `msr` if needed, enables I/O permissions with `ioperm()`, synchronizes, repeatedly emits `out` to port `0xb2`, checks registers on x86_64, increments bogo operations, reports SMI rate, and unloads the module if it loaded it.

## Control Flow

At startup, the stressor probes MSR readability on CPU 0. If the read fails, instance zero attempts to load the `msr` module, but module-load failure is tolerated because only rate reporting depends on MSR reads. The process then enables write access to the APM port with `ioperm(APM_PORT, 2, 1)`. After the stress-ng synchronization barrier, instance zero captures the initial summed SMI count and timestamp when readable.

The main loop snapshots registers on x86_64, executes inline assembly `out %al,%dx` with the no-op SMI command and APM port, snapshots registers again, normalizes expected `rax` and `rdx` differences, reports any other register clobber, and increments the bogo counter. On shutdown it disables I/O permissions, takes a final MSR count, computes SMIs per second per CPU and microseconds per SMI when reliable, and unloads the `msr` module if this run loaded it.

## State and Persistence Behavior

The stressor modifies host-visible state by enabling I/O port permissions for the process and potentially loading/unloading the Linux `msr` kernel module. It stores only local counters, timestamps, and static register snapshots. No files are written. Hardware SMI counts are read from per-CPU MSRs but not persisted.

## Dependencies and Integration Points

The implementation is Linux x86-specific and requires `sys/io.h`, `ioperm()`, in/out assembly support, and stress-ng helpers for capabilities, architecture, CPU count, MSR access, and module management. The exported `stress_smi_info` is `CLASS_CPU | CLASS_PATHOLOGICAL`, `VERIFY_ALWAYS`, and has a `.supported` callback. Nonmatching builds export `stress_unimplemented`.

## Risks and Edge Cases

This is a privileged, pathological hardware stressor. It needs raw I/O and root-level permissions, may trigger firmware paths with platform-specific behavior, and can perturb system latency. The module load/unload path is intentionally best-effort but can race with external module users; `already_loaded` mitigates unloading a preexisting module. SMI count arithmetic assumes final count is not lower than initial count. Register verification is only compiled for x86_64 and intentionally excludes `rax`/`rdx` because the `out` instruction uses them.

## Test Signals

Expected skip behavior is a key test signal: non-root, missing `CAP_SYS_RAWIO`, missing `CAP_SYS_MODULE`, non-x86, or non-Linux builds should skip or register unimplemented. On a suitable x86 Linux test host, a short run should increment bogo operations and print either an SMI rate or a message that `MSR_SMI_COUNT` is unreadable. Verification should not report register clobbering.
