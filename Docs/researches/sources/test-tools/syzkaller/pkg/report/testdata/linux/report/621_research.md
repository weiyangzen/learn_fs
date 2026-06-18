# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/621

## Purpose
This fixture validates a suppressed overlayfs warning in `ovl_create_real`. It also includes noisy userspace segfault and stack-smashing lines before the kernel warning.

## Important APIs, types, and functions
Important frames are `ovl_create_real`, `ovl_workdir_create`, `ovl_make_workdir`, `ovl_get_workdir`, `ovl_fill_super`, `mount_nodev`, `legacy_get_tree`, `vfs_get_tree`, `path_mount`, `__x64_sys_mount`, and `do_syscall_64`.

## Control flow
The log begins with repeated executor userland faults, then an overlayfs mount path warns while creating a real workdir object.

## State and persistence behavior
The expected parser state includes `SUPPRESSED: Y`, meaning the report is recognized but marked suppressed.

## Dependencies and integration points
It connects report parsing with overlayfs mount stacks, userspace-noise filtering, and suppression metadata.

## Risks and test signals
The parser must ignore preamble segfault noise, keep the overlayfs title, and preserve the suppressed flag.
