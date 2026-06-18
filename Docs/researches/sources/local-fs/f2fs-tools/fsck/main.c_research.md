# File Research: sources/local-fs/f2fs-tools/fsck/main.c

Purpose: main entry point and option dispatcher for the fsck-family F2FS tools. One source supports multiple program names: `fsck.f2fs`, `dump.f2fs`, `defrag.f2fs`, `resize.f2fs`, `sload.f2fs`, `f2fslabel`, and optionally `inject.f2fs`.

Key behavior:
- Defines global `struct f2fs_fsck gfsck` and initializes the feature table.
- Provides usage functions for each supported tool mode.
- `f2fs_parse_options()` chooses behavior by `basename(argv[0])`, parses mode-specific flags, sets global configuration `c`, validates device arguments, applies Android default options, and stores per-mode private option structs.
- FSCK mode supports auto/preen/fix policies, cache settings, feature toggles, casefold enablement, quota limit preservation, sparse mode, kernel-version checks, and fault injection settings.
- Dump/defrag/resize/sload/label modes each parse their own option set and update `c`.
- Inject mode is enabled behind `WITH_INJECT`; it initializes `struct inject_option` sentinels and delegates parsing to `inject_parse_options()`.
- `do_fsck()` performs fsck initialization, checkpoint/current-segment checks, optional quota context initialization, orphan/root/tree scans, quota verification, `fsck_verify()`, and maps results to fsck exit codes.
- `do_dump()`, `do_defrag()`, `do_resize()`, `do_sload()`, and `do_label()` wrap mode-specific work.
- `main()` initializes configuration, checks mount state, opens devices, repeatedly mounts via `f2fs_do_mount()`, dispatches by `c.func`, unmounts, optionally reruns fsck after sload or after interactive repair confirmation, finalizes devices, and reports elapsed time.

Important dependencies:
- Calls the mount lifecycle in `mount.c`: `f2fs_do_mount()` and `f2fs_do_umount()`.
- Calls quota functions from `quotaio.h`/`mkquota.c` during fsck.
- Calls mode implementations in other fsck-family files (`fsck.c`, dump/defrag/resize/sload/label/inject code).

Risk notes:
- Program behavior depends heavily on executable name or Android underscore-to-dot rewriting.
- Mounted-device handling is mode-sensitive: dump can proceed differently; fsck on read-only mounted devices disables repair unless forced.
- Sload intentionally remounts by converting itself into an FSCK pass afterward to repair missing quota metadata.
