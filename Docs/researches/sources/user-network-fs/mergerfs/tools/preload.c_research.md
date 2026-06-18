# sources/user-network-fs/mergerfs/tools/preload.c

## Purpose

This file implements a small LD_PRELOAD-style interposer that transparently redirects regular-file opens from the mergerfs mount path to the underlying branch file path. It opens the requested path normally first, asks mergerfs for the backing path through the `user.mergerfs.fullpath` extended attribute, and, when available, reopens the backing file directly. The result is a file descriptor or `FILE*` that bypasses the FUSE layer for subsequent I/O while preserving fallback behavior for unsupported paths or failures.

The interposed entry points are `open`, `open64`, `openat`, `openat64`, `fopen`, `fopen64`, `creat`, and `creat64`. The non-64 variants are compiled only when `_FILE_OFFSET_BITS` is not defined, avoiding duplicate symbol conflicts in large-file builds where libc may map the base names to 64-bit variants.

## Important APIs, types, and functions

`LOAD_FUNC(func)` lazily resolves the next libc symbol with `dlsym(RTLD_NEXT, #func)` and stores it in a static function pointer such as `_libc_open`, `_libc_open64`, `_libc_fopen`, or `_libc_creat64`. It asserts that resolution succeeded, so preload initialization or symbol mismatches fail loudly in debug/runtime assertion-enabled builds.

`get_underlying_filepath` calls `fgetxattr(fd, "user.mergerfs.fullpath", filepath, filepath_size)` and returns the byte count or `-1`. On Linux it includes `<sys/xattr.h>`; on FreeBSD it includes `<sys/extattr.h>`, although the function body still uses the Linux-style `fgetxattr` name. The requested buffer is typically `PATH_MAX`.

`strip_exec` copies an `fopen` mode string while removing any `x` characters. This matters because the original `fopen` may have used exclusive creation mode against the mergerfs path; the second open is against the already-created backing path and should not fail solely because exclusive creation is still present.

The file declares an `IOCTL_BUF`, `IOCTL_APP_TYPE`, and `IOCTL_FILE_INFO`, but these ioctl definitions are unused in the current implementation. The active path discovery mechanism is the mergerfs fullpath xattr.

## Control flow

The `open` and `open64` wrappers follow the same sequence. They resolve libc, extract a variadic `mode_t` when `O_CREAT` or `O_TMPFILE` is present, and call the real libc open on the user path. If the first open fails, the wrapper returns `-1`. If the flags indicate `O_DIRECTORY`, `O_PATH`, or `O_TMPFILE`, the original descriptor is returned immediately. Otherwise the wrapper `fstat`s the descriptor, requires a regular file, asks for `user.mergerfs.fullpath`, clears `O_EXCL` and `O_CREAT`, and opens the real path through libc. If the second open succeeds, it closes the original FUSE descriptor and returns the backing descriptor; if any step fails, it returns the original descriptor.

`openat` and `openat64` mirror the same logic but call `_libc_openat`/`_libc_openat64`. They pass the original `dirfd` to the second `openat` call even when `real_pathname` is populated from an xattr and is expected to be an absolute backing path. If `real_pathname` is absolute this is harmless because `dirfd` is ignored; if it is relative, behavior depends on the caller's directory file descriptor.

`fopen` and `fopen64` open the requested stream normally, get its file descriptor with `fileno`, require a regular file, obtain the fullpath xattr, strip `x` from the original mode string, and open a new stream directly on the underlying path. On success they `fclose` the original stream and return the backing stream; on failure they return the original stream. They do not filter directory-like flags because `fopen` modes target stream files.

`creat` and `creat64` call the libc creation function first, request the underlying fullpath xattr on the returned descriptor, then call libc `creat` again on the underlying path. On success they close the original descriptor and return the backing descriptor. On xattr or second-open failure they return the original descriptor.

## State and persistence behavior

The only persistent process state is the set of static libc function pointers cached after first resolution. The wrappers do not maintain per-file metadata, caches, or locks. They operate entirely on the file descriptor or stream returned by the first libc call and the backing path returned by mergerfs.

Filesystem state can be changed before redirection completes. For creation paths, the original `open`/`creat` against mergerfs may create the file or choose a branch according to mergerfs policy. The second open clears creation and exclusive flags for `open*`, or recreates/truncates through `creat*`, against the backing path. If the second open fails, the caller still receives the original mergerfs descriptor, preserving the visible operation. If the second open succeeds, subsequent I/O is direct to the branch file.

The wrappers deliberately skip `O_TMPFILE`, `O_DIRECTORY`, and `O_PATH` descriptors because they are not normal pathname-backed regular file handles suitable for fullpath redirection. They also skip any descriptor whose `fstat` does not report `S_IFREG`.

## Dependencies and integration points

The preload object depends on dynamic linking (`dlfcn.h`, `RTLD_NEXT`), POSIX file APIs (`open`, `openat`, `creat`, `close`, `fstat`, `fileno`, `fopen`, `fclose`), variadic mode handling, extended attributes, `PATH_MAX`, and standard file status bits. It also relies on mergerfs exposing the `user.mergerfs.fullpath` xattr for opened files.

The integration point is external to mergerfs proper: applications load this object with the dynamic loader so libc file-opening calls are intercepted. Mergerfs still makes initial policy decisions for file creation and path resolution, but the final descriptor can bypass FUSE for read/write I/O. This makes correctness dependent on the runtime config for xattr support and on the kernel/libc symbol names available on the target platform.

## Risks and edge cases

The wrappers use `assert` after `dlsym`; if assertions are disabled, a failed symbol lookup would leave a null function pointer and likely crash when called. There is no synchronization around lazy function-pointer initialization; concurrent first calls may race to write the same pointer, which is usually benign but not formally protected.

`fgetxattr` does not guarantee NUL termination when the value exactly fills the buffer. The code passes `real_pathname` directly to libc open functions without explicitly appending `'\0'` based on the returned byte count. Correctness depends on mergerfs returning a NUL-terminated path or a path shorter than `PATH_MAX` with existing zeroed stack contents, but the stack buffer is not initialized.

`strip_exec` writes into a fixed 64-byte buffer without bounding against unusually long mode strings. Normal `fopen` mode strings are tiny, but a malicious or accidental long mode string could overflow `new_mode`.

For `open*`, the second open removes `O_CREAT` and `O_EXCL` but preserves other flags such as `O_TRUNC`, `O_APPEND`, `O_CLOEXEC`, and access mode. Preserving `O_TRUNC` means a created file may be truncated again on the backing path; normally this is equivalent, but it matters for races. For `creat*`, the backing `creat` also truncates. The gap between original and backing opens can expose races if another process renames, removes, or changes the file.

The FreeBSD include branch is incomplete-looking because it includes `<sys/extattr.h>` but calls `fgetxattr`, and `O_PATH` may not exist on non-Linux platforms. The file defines `O_TMPFILE` to zero on FreeBSD, but not `O_PATH`, so portability depends on platform headers or build flags.

`openat*` passes `dirfd_` for the second open. This is safe for absolute backing paths but could be surprising if the xattr value is relative. The unused ioctl declarations suggest either a previous or planned fullpath lookup method and should not be mistaken for active behavior.

## Test signals

This file has no direct tests in the same source. Useful test signals would include an LD_PRELOAD integration test that opens regular files through a mergerfs mount and verifies `/proc/self/fd/<fd>` or equivalent resolves to a branch path; fallback tests where the xattr is unavailable; creation tests for `O_CREAT`, `O_EXCL`, `O_TRUNC`, `creat`, and `fopen` modes containing `x`; and negative tests for directories, `O_PATH`, `O_TMPFILE`, non-regular files, and paths longer than or equal to `PATH_MAX`.

Because the code is failure-tolerant by design, tests should verify both success redirection and exact fallback behavior. The most important safety signals are no descriptor leaks when the second open succeeds, no close of the original descriptor when the second open fails, correct propagation of libc `errno` for initial failures, and correct behavior when `user.mergerfs.fullpath` is missing or disabled by xattr configuration.
