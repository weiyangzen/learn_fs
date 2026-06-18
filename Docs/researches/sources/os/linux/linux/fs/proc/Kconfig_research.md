# File Research: sources/os/linux/linux/fs/proc/Kconfig

## Purpose
Defines Kconfig options controlling procfs availability and optional procfs features.

## Main Options
- `PROC_FS`: core `/proc` filesystem support, default enabled.
- `PROC_KCORE`: live kernel ELF core file at `/proc/kcore`.
- `PROC_VMCORE`: crash dump image export at `/proc/vmcore`.
- `PROC_VMCORE_DEVICE_DUMP`: optional device firmware/hardware dump notes in vmcore.
- `NEED_PROC_VMCORE_DEVICE_RAM` and `PROC_VMCORE_DEVICE_RAM`: support adding RAM discovered by devices such as virtio-mem to vmcore.
- `PROC_SYSCTL`: `/proc/sys` sysctl interface.
- `PROC_PAGE_MONITOR`: process/page monitoring files such as smaps, clear_refs, pagemap, kpagecount, and kpageflags.
- `PROC_CHILDREN`: optional `/proc/<pid>/task/<tid>/children`.
- `PROC_PID_ARCH_STATUS`: arch-specific pid status hook.
- `PROC_CPU_RESCTRL`: CPU resource control proc status hook.

## Dependencies and Integration
Options depend on broader kernel facilities including `MMU`, `CRASH_DUMP`, `VIRTIO_MEM`, `SYSCTL`, and `PROC_FS`. The Makefile consumes these symbols to include optional procfs object files.

## Risks and Review Hotspots
- Several procfs interfaces expose sensitive memory, process, or crash data; Kconfig dependencies and defaults materially affect attack surface.
- Disabling procfs or sysctl can break userspace expectations.
- `PROC_PAGE_MONITOR` gates interfaces used by monitoring/debugging tools but also exposes memory layout and page state information.
