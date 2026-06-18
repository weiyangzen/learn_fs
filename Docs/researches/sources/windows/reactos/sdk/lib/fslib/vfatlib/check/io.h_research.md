# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/io.h

Declares the checker’s virtual disk I/O API.

Key elements:
- `fs_open` has a Unix path signature outside ReactOS and a `PUNICODE_STRING` volume-root signature in ReactOS.
- Core APIs: `fs_read`, `fs_test`, `fs_write`, `fs_close`, `fs_changed`.
- ReactOS-only APIs: `fs_isdirty`, `fs_lock`, `fs_dismount`.

Dependencies:
- Relies on `off_t`; on ReactOS this is provided through the broader included checker/library headers.
- Publicly mirrors the implementation in `io.c`.

Research notes:
- This header abstracts checker code from immediate vs deferred write behavior.
- ReactOS additions expose Windows volume lifecycle operations needed by `VfatChkdsk`.
