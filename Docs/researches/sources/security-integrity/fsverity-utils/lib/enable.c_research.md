# sources/security-integrity/fsverity-utils/lib/enable.c

Purpose: This library file wraps the Linux `FS_IOC_ENABLE_VERITY` ioctl for enabling fs-verity on an open file, optionally with a built-in signature.

Important APIs and functions: `libfsverity_enable()` delegates to `libfsverity_enable_with_sig()` with no signature. `libfsverity_enable_with_sig()` validates params, applies default hash algorithm and block size, fills `struct fsverity_enable_arg`, attaches optional signature pointer/size, and invokes `ioctl`.

Control flow and state: The function does not persist user-space state. Kernel state changes when the ioctl succeeds: the target file becomes fs-verity protected and immutable for content changes.

Dependencies and integration points: Integrates public parameters with `fsverity_uapi.h`, kernel fs-verity support, and CLI `enable`.

Risks and test signals: Argument validation must match kernel expectations without rejecting valid future callers. Risks include pointer-size casting, invalid block sizes, unsupported kernels, and signature size overflow. Signals are ioctl integration tests, expected negative errno returns, and CLI enable behavior on supported filesystems.
