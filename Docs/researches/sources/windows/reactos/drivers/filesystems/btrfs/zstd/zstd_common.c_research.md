# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_common.c

Read completely: 74 lines.

Small common implementation file for the vendored zstd library. It includes `<stdlib.h>`, `<string.h>`, `error_private.h`, and `zstd_internal.h`, then provides externally visible version, error, and custom-allocation helper functions.

Exports:
- `ZSTD_versionNumber()` returns `ZSTD_VERSION_NUMBER`.
- `ZSTD_versionString()` returns `ZSTD_VERSION_STRING`.
- `ZSTD_isError()` forwards to `ERR_isError()` after undefining the internal macro of the same name.
- `ZSTD_getErrorName()`, `ZSTD_getErrorCode()`, and `ZSTD_getErrorString()` forward to private error helpers.
- `ZSTD_malloc()`, `ZSTD_calloc()`, and `ZSTD_free()` call the `ZSTD_customMem` allocator/free callbacks.

Behavior notes:
- `ZSTD_calloc()` implements zero-initialization as `customAlloc()` followed by `memset(ptr, 0, size)`.
- `ZSTD_free()` skips the callback when `ptr == NULL`.
- The file assumes the effective `ZSTD_customMem` callbacks are valid. In this ReactOS vendored build, integration must ensure default/custom allocator plumbing never passes a null allocation callback into these helpers.

Risks/quirks:
- `ZSTD_calloc()` does not check whether `customAlloc()` returned `NULL` before calling `memset()`. That matches this vendored upstream code path but means callers/allocation wrappers must avoid invoking it with failing or absent allocators, or the build must provide an internal defaulting layer before this helper is reached.
- No filesystem-specific logic lives here; its role is shared zstd support for the broader Btrfs compression/decompression code.
