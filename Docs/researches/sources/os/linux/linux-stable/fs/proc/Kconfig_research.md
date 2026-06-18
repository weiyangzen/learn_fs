# File Research: sources/os/linux/linux-stable/fs/proc/Kconfig

## Purpose

Defines kernel configuration options for procfs and optional procfs-backed features.

## Main Options

- `PROC_FS`
  - Enables `/proc`.
  - Defaults to yes.
  - Described as a virtual filesystem that generates information dynamically.
- `PROC_KCORE`
  - Enables `/proc/kcore` live kernel ELF core view.
  - Depends on `PROC_FS && MMU`.
  - Selects `VMCORE_INFO`.
- `PROC_VMCORE`
  - Enables `/proc/vmcore` crash dump image export.
  - Depends on `PROC_FS && CRASH_DUMP`.
  - Defaults to yes.
- `PROC_VMCORE_DEVICE_DUMP`
  - Allows device hardware/firmware logs to be added as ELF notes to `/proc/vmcore`.
  - Depends on `PROC_VMCORE`.
- `NEED_PROC_VMCORE_DEVICE_RAM`
  - Internal bool selected by architectures.
- `PROC_VMCORE_DEVICE_RAM`
  - Includes device-provided RAM ranges, such as virtio-mem, in crash dump metadata.
  - Depends on `PROC_VMCORE`, `NEED_PROC_VMCORE_DEVICE_RAM`, and `VIRTIO_MEM`.
- `PROC_SYSCTL`
  - Enables `/proc/sys`.
  - Depends on `PROC_FS`, selects `SYSCTL`, defaults to yes.
- `PROC_PAGE_MONITOR`
  - Enables memory monitoring proc files such as `smaps`, `clear_refs`, `pagemap`, `kpagecount`, and `kpageflags`.
  - Depends on `PROC_FS && MMU`, defaults to yes.
- `PROC_CHILDREN`
  - Enables `/proc/<pid>/task/<tid>/children`.
  - Depends on `PROC_FS`, defaults to no.
- `PROC_PID_ARCH_STATUS`
  - Architecture-specific proc pid status support, default no.
- `PROC_CPU_RESCTRL`
  - CPU resource control proc status support, default no.

## Notes

This file controls build-time availability of many entries referenced by `fs/proc/base.c`, `array.c`, and the proc Makefile.
