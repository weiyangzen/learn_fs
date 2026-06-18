# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/main.c

## Purpose

Machine-independent kernel startup path. It initializes core kernel subsystems, mounts root, prepares process 0, creates init/pageout/fsflush/cluster processes, starts selected system threads, and enters the scheduler.

It also builds the initial user stack and exec state for `/sbin/init` or zone init.

## Main Responsibilities

- Maintain well-known process globals: `proc_sched`, `proc_init`, `proc_pageout`, `proc_fsflush`.
- Define global memory counters `maxmem`, `freemem`, and startup state `interrupts_unleashed`.
- Provide process-zero static LWP directory/hash storage.
- Construct init argument stack and invoke `exec_common()`.
- Initialize init process address-space model and protections.
- Drive the ordered kernel bootstrap sequence in `main()`.
- Create init, pageout, fsflush, optional cluster process, and p0 system threads.
- Initialize process 0’s LWP directory and tid hash.

## Key Entry Points

- `cluster_wrapper()`
  Invokes `cluster()` and panics if it returns.

- `exec_init(const char *initpath, const char *args)`
  Builds the initial user stack layout for init, including argv strings and pointers, handles ILP32 argv packing, sets syscall argument state for `execve`, clears inherited signal mask, and retries selected transient `exec_common()` failures.

- `start_init_common()`
  Common global-zone and non-global-zone init setup. Establishes init pid in zone, resets accounting, creates address space, sets 32-bit model/user limits/protections, initializes core state, and calls `exec_init()`.

- `start_init()`
  Sets `proc_init`, starts global init, and enters `lwp_rtt()` after successful exec setup.

- `main(void)`
  Top-level MI kernel startup routine.

## Startup Ordering Highlights

`main()` performs a strict sequence:

1. Takes `ualock` to prevent administrative shutdown during boot.
2. Initializes lgroup stage 2.
3. Runs `startup()`, `segkmem_gc()`, callback/cyclic/callout/clock setup.
4. Reinitializes microstate counters after final time source selection.
5. Initializes lgroup stage 3 and calls `init_tbl`.
6. Loads iSCSI boot properties, initializes VM and physio buffers.
7. Drops to `spl0()` and sets `interrupts_unleashed`.
8. Creates `process_cache`.
9. Mounts root via `vfs_mountroot()`.
10. Initializes error queues, CPU kstats, timestamps, post-startup, swap state, audit.
11. Starts vmem periodic rescale and optionally plumbs networking.
12. Configures console, releases bootstrap memory, force-attaches drivers.
13. Calls `setupclock()`.
14. Initializes p0 LWP directory/hash and inserts current thread.
15. Initializes extended accounting and sysevent channel threads.
16. Completes lgroup and MP initialization.
17. Starts platform post-startup hooks and SMT late init on x86.
18. Creates init, pageout, fsflush, and optional cluster processes.
19. Starts module uninstall and seg_pasync p0 threads.
20. Releases `ualock`, labels p0 as `sched`, and enters `sched()`.

## Important Data

- `initname`, `initargs`
  Default init path and boot args.

- `p0_lwpdir[2]`, `p0_tidhash[2]`, `p0_lep`
  Static initial LWP directory/hash resources for process 0.

- `process_cache`
  Kmem cache for `proc_t`.

## Locking and Synchronization

- `ualock` blocks disruptive administrative actions during startup.
- p0 LWP directory initialization occurs after `setupclock()` and before accounting/sysevent and process creation.
- Interrupts are only unleashed after clock/callout/cyclic setup and before root mount and driver activity requiring interrupts.

## Init Stack Construction

`exec_init()` treats boot args as space-delimited tokens with no quoting support. It copies the combined init path and args string to the top of the user stack, builds argv pointers beneath it, converts argv to 32-bit pointers for ILP32 processes, and sets current LWP syscall state so `exec_common()` sees an `execve`-style call.

## External Dependencies

Boot properties, VFS root mount, VM, HAT, lgroup, callouts/cyclics, DDI, audit, STREAMS plumbing, module subsystem, scheduler, pageout, fsflush, sysevent, fastboot, SMT, and process creation.

## Research Notes

This file is mostly sequencing glue. Bugs here are usually ordering bugs: using a subsystem before its clock/callout/root/VM/driver prerequisite, or allowing shutdown/admin interference during boot. The p0 LWP directory setup is also a direct dependency of LWP lookup semantics used elsewhere.
