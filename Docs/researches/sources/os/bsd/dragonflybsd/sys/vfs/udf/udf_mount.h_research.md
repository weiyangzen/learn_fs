# File Research: sources/os/bsd/dragonflybsd/sys/vfs/udf/udf_mount.h

User/kernel mount-argument structure for the UDF filesystem.

Key responsibilities:
- Defines `struct udf_args`, carrying the user-supplied block special device path, network export options, and mount flags.
- Provides the mount argument ABI consumed by `udf_mount` in `udf_vfsops.c`.

Dependencies:
- Uses `struct export_args` from DragonFly mount/export infrastructure.
- The `fspec` pointer is copied from userland by mount code.

Notable risks:
- This is ABI-facing for mount tooling; field order and type changes affect userland compatibility.
- `fspec` is a user pointer and requires careful `copyin`/`copyinstr` handling by callers.
