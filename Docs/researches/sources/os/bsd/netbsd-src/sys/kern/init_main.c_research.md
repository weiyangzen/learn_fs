# File Research: sources/os/bsd/netbsd-src/sys/kern/init_main.c

## Purpose
Primary machine-independent NetBSD kernel startup path: initializes core subsystems, configures devices, mounts root, creates init, starts kernel daemons, and enters the scheduler.

## Main Interfaces
- `main()` performs kernel initialization sequencing from console setup through `uvm_scheduler()`.
- `configure()`, `configure2()`, and `configure3()` split autoconfiguration into early hardware probing, post-CPU/device setup, and mountroot-dependent callbacks.
- `rootconf()` and `rootconf_handle_wedges()` choose root devices, including disk wedge translation.
- `start_init()` waits for root readiness, constructs a small user stack, and tries `/sbin/init`, `/sbin/oinit`, `/sbin/init.bak`, and `/rescue/init`.
- `check_console()` verifies `/dev/console`.
- `calc_cache_size()` computes cache sizing bounded by physical memory and virtual address space.
- `banner()` prints the startup memory/version banner.

## Dependencies
Touches nearly every kernel subsystem: console, locks, UVM, sysctl, kauth/secmodel, modules, buffers, VFS, file descriptors, kqueue, tty, networking, autoconf, random/CPRNG, scheduler, CPU topology, Veriexec, PaX, accounting, ktrace, root mount, and process exec.

## Implementation Notes
Ordering is the core design. The file creates process 0, disables preemption during boot, initializes VFS and devices before root mount, creates process 1 early but gates its exec using `start_init_exec`, finalizes modules/configuration before root selection, then starts pageout and syncer threads.

## Research Notes
This file is the boot choreography. Changes must preserve initialization ordering, especially around sysctl setup, module class initialization, autoconfiguration, root mount, `initproc` race avoidance, preemption enablement, and the point at which process 1 is allowed to exec.
