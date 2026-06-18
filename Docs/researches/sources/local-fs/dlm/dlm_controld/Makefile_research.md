# File Research: sources/local-fs/dlm/dlm_controld/Makefile

## Purpose
Build and install rules for the `dlm_controld` daemon binary and `libdlmcontrol` shared library.

## Main Behavior
- Builds `dlm_controld` from daemon sources including membership, CPG, configfs/sysfs action code, fencing, plock, config, logging, member, and node config modules.
- Builds `libdlmcontrol.so.3.2` from `lib.c`, with symlinks `libdlmcontrol.so` and `libdlmcontrol.so.3`.
- Generates `libdlmcontrol.pc` from `libdlmcontrol.pc.in` by substituting prefix and library directory.
- Applies hardened compiler/linker defaults: `_FORTIFY_SOURCE=2`, stack protector, stack clash protection, PIE for the daemon, relro/now, and extensive warning flags.
- Uses `pkg-config` to discover Corosync libraries (`libcpg`, `libcmap`, `libcfg`, `libquorum >= 3.1.0`) and optionally `libsystemd` when `USE_SD_NOTIFY=yes`.
- Installs daemon, shared library, symlinks, pkg-config file, header, and man pages under configurable `DESTDIR`, `PREFIX`, `BINDIR`, `LIBDIR`, `HDRDIR`, `MANDIR`, and `PKGDIR`.

## Integration Points
- Includes headers from `../include` and `../libdlm`.
- Links daemon with pthread, rt, uuid, Corosync, and optionally systemd.
- Exported control library ABI is versioned as major 3, minor 2.

## Risks and Notes
- The makefile compiles all daemon sources in one compiler invocation rather than object-by-object, so incremental rebuilds are coarse.
- It uses GNU make `.SHELLSTATUS` after `$(shell pkg-config ...)`; non-GNU make would not work.
- `LIB_LDFLAGS` includes `-pie` even for shared library linking; this is inherited local style and should be tested before changing.
