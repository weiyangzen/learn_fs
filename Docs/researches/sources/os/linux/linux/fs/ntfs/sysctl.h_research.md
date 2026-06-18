# File Research: sources/os/linux/linux/fs/ntfs/sysctl.h

Read coverage: complete file, 26 lines.

This header declares or stubs the NTFS debug sysctl hook.

Key logic:
- If `DEBUG && CONFIG_SYSCTL`, declares `int ntfs_sysctl(int add);`.
- Otherwise provides an inline `ntfs_sysctl()` that always returns success.

Integration:
- Lets `super.c` call `ntfs_sysctl(1)` and `ntfs_sysctl(0)` unconditionally without scattering preprocessor conditionals.
- Keeps non-debug and non-sysctl builds free of runtime behavior.

Risk:
- Minimal. The stub intentionally ignores `add`.
