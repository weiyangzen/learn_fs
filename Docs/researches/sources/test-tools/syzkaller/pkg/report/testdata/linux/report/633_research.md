# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/633

## Purpose
This fixture covers a corrupted KMSAN uninitialized-value report in `prepend_path`.

## Important APIs, types, and functions
Important frames include `prepend_path`, `d_absolute_path`, `tomoyo_realpath_from_path`, `tomoyo_path_number_perm`, `tomoyo_path_mknod`, `security_path_mknod`, `path_openat`, `do_filp_open`, and `__x64_sys_open`.

## Control flow
A path creation/open operation passes through TOMOYO security hooks, path rendering calls `prepend_path`, and KMSAN reports uninitialized data. Stack depot origin lookup also warns, marking the report corrupted.

## State and persistence behavior
The fixture stores both the KMSAN diagnostic and secondary stack-depot warning. `CORRUPTED: Y` is expected persisted metadata.

## Dependencies and integration points
It integrates KMSAN parsing with VFS path generation and LSM/TOMOYO call stacks.

## Risks and test signals
The parser must attribute the bug to `prepend_path` and retain KMSAN type despite the secondary warning.
