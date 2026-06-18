# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_shutdown.c

## Purpose

`kern_shutdown.c` implements DragonFlyBSD's machine-independent reboot, shutdown, panic, kernel dump, and panic-notification path. It coordinates orderly sync/unmount behavior, panic-time CPU ownership, dump-device setup, registered shutdown event handlers, and final halt/reset behavior.

## Main Contents

- Shutdown registration:
  - `shutdown_conf()` registers final-stage handlers for poweroff delay, halt prompt, panic reboot delay, and reset.
  - `shutdown_nice()` records requested reboot flags and signals `init` with `SIGINT`, or directly boots with `RB_NOSYNC` if init is absent.
- Reboot path:
  - `sys_reboot()` checks reboot capability and calls `boot()`.
  - `boot()` raises priority, migrates shutdown to CPU 0 when possible, invokes shutdown eventhandler stages, cleans process filesystem references, syncs disks, optionally unmounts filesystems, performs dumps, and finally invokes reset/halt handlers.
- Sync accounting:
  - `shutdown_busycount1()` counts locked or delayed-write buffers except TMPFS.
  - `shutdown_busycount2()` narrows late counting to buffers with active write I/O and ignores TMPFS/NFS/MFS/SMBFS, printing stuck buffers after many iterations.
- Final handlers:
  - `shutdown_halt()` handles `RB_HALT`.
  - `shutdown_panic()` implements panic reboot delay and console abort.
  - `shutdown_reset()` calls `cpu_reset()`.
  - `poweroff_wait()` implements `kern.shutdown.poweroff_delay`.
- Dump configuration:
  - `mkdumpheader()` fills `kerneldumpheader`.
  - `setdumpdev()`, `dump_conf()`, and `sysctl_kern_dumpdev()` configure `dumpdev`.
  - `set_dumper()` registers one active dumper.
  - `dumpsys()` invokes `md_dumpsys()` unless already dumping or running as a vkernel.
- Panic path:
  - `panic()` serializes panic ownership through `panic_cpu_gd`, saves held token metadata, releases all tokens, resets spinlock accounting, formats and prints the panic, notifies optional panic hooks, handles watchdog/GPIO hooks, optionally enters DDB or stops other CPUs, and calls `boot(RB_AUTOBOOT | RB_DUMP | optional RB_NOSYNC)`.
- Shutdown support:
  - `shutdown_cleanup_proc()` releases process cwd/root/jail dirs, text vnode/namecache refs, vkernel state, and user VM mappings.
  - `shutdown_kproc()` asks system kthreads to suspend during shutdown.
  - `dump_reactivate_cpus()` restarts stopped CPUs after requesting user reschedule.

## State And Interfaces

The file owns global shutdown state such as `panicstr`, `dumping`, `dumpdev` setup, `bootverbose`, `cold`, `panic_cpu_gd`, panic token snapshots, and dump compatibility values. It exposes sysctls under `debug`, `kern`, `kern.shutdown`, and `machdep`, and uses eventhandler stages `shutdown_pre_sync`, `shutdown_post_sync`, and `shutdown_final`.

## Dependencies And Risks

The code sits at the intersection of VFS, buffer cache, process state, CPU control, console I/O, watchdog/panic notifiers, and dump devices. Shutdown cleanup intentionally drops process references and user mappings late in system life, so ordering matters. The panic path deliberately overrides normal lock/token rules; regressions here can deadlock secondary panics, lose dump state, or recurse while printing/dumping.
