# sources/sync-backup/borg/src/borg/platform/xattr.py

Purpose: shared low-level helpers for platform xattr modules, especially buffer sizing and errno conversion.

Important APIs/types: `split_string0`, `split_lstring`, `BufferTooSmallError`, `_check`, `_listxattr_inner`, `_getxattr_inner`, and `_setxattr_inner`. A global reusable `Buffer` is capped at `2**24`.

Control flow/state: list/get helpers call platform C wrappers, double buffer size on `ERANGE` or full-buffer truncation, and return byte count plus buffer. `_check` maps negative return values through platform `get_errno` to `OSError` or retry. Set helper calls once and propagates errors.

Dependencies/integration: used by Linux/Darwin/FreeBSD/NetBSD xattr implementations and imported by `platform.__init__` for packaging.

Risks: large xattrs can drive buffer growth to the cap. `split_lstring` trusts length prefixes. Correct errno handling depends on platform `get_errno`. Full-buffer retry is conservative.

Test signals: splitting formats, ERANGE retry, full-buffer retry, FD path formatting, invalid errno handling, and set error propagation.
