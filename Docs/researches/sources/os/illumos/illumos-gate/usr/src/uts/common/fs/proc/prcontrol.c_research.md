# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prcontrol.c

## Role

Implements `/proc` control writes. User processes write command records to `/proc/<pid>/ctl` or lwp control files, and this file parses those records, locks the target process/lwp, and applies control operations such as stop, run, signal control, register writes, watchpoints, agent lwp creation, address-space I/O, credential mutation, privilege mutation, and zone credential changes.

## Major Responsibilities

- Defines command sizing metadata for native and ILP32 `/proc` control commands.
- Buffers and validates one or more control records from a `uio_t`.
- Handles variable-size commands such as `PCSCREDX`, `PCSPRIV`, and `PCSXREG`.
- Provides native and 32-bit command interpreters.
- Applies process/lwp stop and run controls.
- Changes signal masks, pending/current signals, fault masks, syscall tracing masks, and `/proc` flags.
- Writes general, floating-point, extra register, and resume-address state.
- Creates `/proc` agent lwps.
- Reads/writes target address spaces through `prusrio()`.
- Changes process credentials, privileges, and temporary zone credentials.
- Manages watchpoint setup/cancelation by pausing lwps and editing watched areas.

## Command Parsing

`prwritectl_common()` is the shared parser for native and ILP32 writes. It reads enough data to identify a command, consults `proc_control_info_t`, reads static and dynamic payload sizes, rounds records as required by `/proc` ABI rules, locks the target, and invokes either `pr_control()` or `pr_control32()`.

Important details:

- It unlocks the target before `uiomove()` or buffer reallocation to avoid holding process locks across memory allocation or user I/O.
- It supports multiple commands in a single write.
- It handles ILP32 payload alignment by copying unaligned data to a temporary aligned buffer when needed.
- A positive command error stops the batch. A `-1` return means a timeout or special wait condition occurred after unlock, and processing may continue according to caller semantics.

## Native And 32-bit Control

`pr_control()` handles native command payloads. `pr_control32()` converts 32-bit structures and rejects commands that cannot apply to non-32-bit targets with `EOVERFLOW`. Both reject system processes and both unlock the `prnode_t` before returning most command errors.

The command tables cover `PCSTOP`, `PCDSTOP`, `PCWSTOP`, `PCTWSTOP`, `PCRUN`, signal operations, syscall entry/exit masks, flags, register writes, watchpoints, agent creation, address-space read/write, credentials, privileges, and zone changes.

## Stop/Run Logic

- `pr_stop()` marks target lwps with `TP_PRSTOP`, wakes interruptible waits, sets virtual stops where appropriate, pokes threads into the kernel, and broadcasts `p_holdlwps`.
- `pr_wait_stop()` waits until the selected lwp or process representative is stopped, honoring optional millisecond timeouts.
- `pr_setrun()` validates stopped state, handles signal/fault clearing, single-step setup, directed stop, syscall abort, agent-lwp restrictions, representative-lwp demotion, and process-wide resume.
- `allsetrun()` clears `/proc` stop flags and sets all stopped lwps runnable.
- `pr_wait_die()` waits after `SIGKILL` so later operations see target disappearance.

## Signal, Fault, And Trace Control

- `pr_settrace()` sets the signal trace mask and toggles `P_PR_TRACE`.
- `pr_setsig()` installs or clears the current signal on the selected lwp, updates siginfo, handles zone id normalization, and applies SIGKILL/SIGCONT/jobcontrol side effects.
- `pr_kill()` queues a signal with caller pid/uid/zone metadata.
- `pr_unkill()` removes pending non-SIGKILL signals.
- `pr_setentryexit()` updates syscall entry/exit masks and toggles syscall tracing.
- `pr_sethold()` changes an lwp hold mask and wakes it if newly unblocked signals are pending.
- `pr_setfault()`, `pr_clearsig()`, and `pr_clearflt()` update fault/signal stop state.

## Register And Address Controls

Register writes require the selected lwp to be stopped, virtually stopped, or directed-stopped. The code drops `p_lock` before touching lwp register state because target stacks or register save areas may page fault.

Handled state includes general registers, fp registers, machine-dependent xregs, and saved resume address.

## Watchpoints

`pr_watch()` validates ranges and flags, clamps to user address limit, limits page span, and forces the process to be fully stopped. For self-watch operations it uses `holdwatch()`/`continuelwps()`. For other processes it pauses lwps with `pauselwps()`, waits for all to stop, then drops `p_lock` while setting or clearing watched areas.

`pr_cancel_watch()` performs similar pausing and then frees all watchpoints, disables watch state on threads, and restores page protections.

## Agent LWP

`pr_agent()` creates the special `/proc` agent lwp only when the target is fully stopped or directed-stopped and has no existing agent. It builds the lwp stopped, copies supplied registers, records spymaster `psinfo`, mirrors scheduling-class state, publishes `p_agenttp`, starts the lwp, and waits until the agent stops on `PR_REQUESTED`.

## Credential, Privilege, And Zone Mutation

- `pr_scred()` validates uid/gid values, checks setid policy, duplicates and replaces process credentials, updates uid process counts, and marks all threads to refresh credentials on syscall entry.
- `pr_spriv()` delegates privilege mutation to `priv_pr_spriv()` and marks threads for credential refresh.
- `pr_szoneid()` allows privileged temporary credential transitions only between the process zone and global zone, updates zone uid counts, and marks threads for refresh.

## Research Notes

This file is the procedural heart of procfs control. Its central engineering constraint is lock choreography: many commands must hold enough process state stable to be meaningful, but must drop locks before user I/O, allocation, register access, address-space I/O, or operations that may sleep.
