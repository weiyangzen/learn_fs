# sources/test-tools/stress-ng/stress-efivar.c

Purpose: implements `efivar`, which reads UEFI variable entries from Linux sysfs (`/sys/firmware/efi/efivars` or legacy `/sys/firmware/efi/vars`) to stress EFI variable filesystem read paths and related fd operations.

Important APIs/types/functions: `stress_efi_var_t` mirrors legacy raw variable layout. `efi_var_ignore()` skips dot entries and sensitive/control variables. `guid_to_str()` and `efi_get_varname()` decode legacy raw metadata. `efi_get_data()` reads individual legacy fields. `efi_read_variable()` reads a variable file, gathers fdinfo, probes lseek/mmap/ioctl helpers, and optionally gets/sets FS flags. `efi_vars_get()` iterates cached dentries. `stress_efivar_supported()` checks sysfs availability/capability. `stress_efivar()` handles scanning, shared ignore map, forked worker, metrics, and cleanup.

Control flow: support selection prefers `efivars` over legacy `vars`. At runtime the stressor scans the chosen directory, maps a shared `efi_ignore[]` bitmap, synchronizes, then forks a child. The child applies failure/scheduler/OOM settings and repeatedly calls `efi_vars_get()`, which skips ignored names, reads data through the appropriate backend, marks failing or empty legacy entries ignored, increments bogo count, and accumulates read metrics.

State and persistence behavior: directory entries are cached in memory; per-variable ignore state lives in shared anonymous mmap named `efi-ignore-state`. The stressor is read-oriented, but `efi_read_variable()` may call `FS_IOC_SETFLAGS` with the existing flags value, intended to be non-mutating. No EFI variables are created or deleted.

Dependencies and integration points: Linux-only except Alpha exclusion; uses capabilities checks, OOM and killpid helpers, madvise/signal helpers, sysfs file reads, fdinfo, and metrics. Registered as `CLASS_OS` with `VERIFY_ALWAYS`.

Risks: EFI variable access can require privileges and may expose firmware/kernel bugs. Even read-like operations on efivarfs are sensitive; the code avoids `new_var`, `del_var`, `MokListRT`, writes no data, and uses a child for containment. Directory contents can change while scanned, so open/read failures are usually ignored or mark entries ignored.

Test signals: run on systems with no EFI, legacy vars, and efivars; verify support skip messages, raw data read rate metrics, no variable mutations, and correct cleanup of dirent lists and shared ignore mmap.
