# sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/uapi/file_operations.h

Purpose: this UAPI fixture defines ioctl command constants and a payload struct for file-operation extraction tests.

Important APIs and flow: includes `ioctl.h`, defines `FOO_IOCTL1` through `FOO_IOCTL9` with `_IO`, `_IOR`, `_IOW`, and `_IOWR`, declares enum constants `FOO_IOCTL10` and `FOO_IOCTL11`, and defines `struct foo_ioctl_arg { int a, b; }`.

State and persistence: static declarations only.

Dependencies and integration: included by `file_operations.c` and `scopes.c`. Its constants are expected to surface in golden JSON and generated syzkaller descriptions when reachable.

Risks: numeric values depend on the local `_IOC` macro definitions and `sizeof` behavior for fixture types.

Test signals: validates ioctl direction/size extraction, enum and macro constants, and struct argument layout.
