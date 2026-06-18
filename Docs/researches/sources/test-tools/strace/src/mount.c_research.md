<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mount.c -->
# sources/test-tools/strace/src/mount.c

Purpose: decodes legacy `mount` syscall arguments and flags.
Important APIs/types/functions: `SYS_FUNC(mount)`, `mount_flags`, `MS_MGC_VAL`, `MS_MGC_MSK`, `printpath`, and `printstr`.
Control flow: prints source, target, filesystem type, strips old magic flag bits when present, prints flags, and prints data as string/address depending on verbosity and pointer. State and persistence behavior: none.
Dependencies and integration points: filesystem syscall decoding. Risks: old magic mask handling must not hide real flags. Test signals: bind/remount/readonly flags, old magic value, null data, and unknown flag traces.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mount.c -->
