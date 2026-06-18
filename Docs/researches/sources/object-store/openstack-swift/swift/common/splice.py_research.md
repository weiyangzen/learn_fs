# sources/object-store/openstack-swift/swift/common/splice.py

## Purpose

This module provides small `ctypes` bindings for Linux `tee(2)` and `splice(2)`. Swift can use these zero-copy system calls to move data between file descriptors or duplicate pipe buffers without copying data through Python user space. The module exports instantiated callable objects, `tee` and `splice`, rather than the binding classes themselves.

## Important APIs, types, and functions

`tee(fd_in, fd_out, len_, flags)` wraps libc `tee`. File descriptors may be integer FDs or objects with `fileno()`. `flags` may be an integer bitmask or an iterable of flag constants. The call returns the kernel byte count. `tee.available` reports whether libc exposed the symbol on the current platform.

`splice(fd_in, off_in, fd_out, off_out, len_, flags)` wraps libc `splice`. It exposes `SPLICE_F_MOVE`, `SPLICE_F_NONBLOCK`, `SPLICE_F_MORE`, and `SPLICE_F_GIFT` constants copied from Linux fcntl headers. Offset arguments are either integer offsets, which are passed by pointer and returned with updated values, or `None`, which passes NULL and lets the kernel update the file offset. The return value is `(result, off_in_value, off_out_value)`.

`c_loff_t` is defined as `ctypes.c_long` and is used for offset pointers. Each wrapper installs `argtypes`, `restype`, and an `errcheck` callback on the libc function.

## Control flow

At import time the module instantiates `Tee()` and `Splice()`, loads libc with `ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)`, and looks for the relevant symbols. Missing symbols result in `_c_tee` or `_c_splice` being set to `None`; calls then raise `EnvironmentError` rather than failing during import. Present symbols are configured once, and every later call normalizes flags, obtains integer file descriptors, creates optional offset pointers, and invokes libc.

The errcheck path converts a kernel return value of `-1` into `IOError(errno, "...")`; successful `tee` returns the raw byte count, while successful `splice` returns the byte count plus possibly updated offsets.

## State and persistence behavior

The only module state is the two singleton binding objects and their cached libc function pointers. There is no persistent storage. Calls can change kernel-maintained file offsets when `off_in` or `off_out` is `None`, and can update explicit offset pointer values when offsets are supplied. The Python wrapper itself does not cache buffers or file descriptors.

## Dependencies and integration points

The module depends on Linux/glibc-like libc support, `ctypes`, and `os.strerror`. It is designed as a low-level optional accelerator for higher-level Swift data paths. Consumers must check `.available` or handle `EnvironmentError` when running on platforms without `tee` or `splice`.

## Risks and edge cases

The errno handling appears suspicious: `ctypes.set_errno(0)` sets errno to zero and returns the previous ctypes errno, but the usual pattern is `ctypes.get_errno()`. Tests should verify that raised `IOError.errno` is meaningful on failure. `c_loff_t = ctypes.c_long` assumes a compatible offset width; that is appropriate on common 64-bit Linux but should be validated on less common ABI targets. The wrappers do not retry on `EINTR` or handle partial transfers; callers must be prepared for short counts and nonblocking errors.

`tee` and `splice` require particular FD types, especially pipes for many operation modes. The Python signature does not enforce these constraints, so misuse is reported by the kernel. Passing `0` for offsets is not the same as passing `None`, and the docstring explicitly warns callers to use `None` for NULL offset pointers.

## Test signals

Tests should cover import on systems with and without libc symbols, `.available`, flag list folding, integer and file-object descriptors, explicit offset return values, NULL offset behavior, and error propagation with invalid descriptors. Integration tests can use pipes and temporary files to confirm byte movement while checking for partial-transfer semantics.
