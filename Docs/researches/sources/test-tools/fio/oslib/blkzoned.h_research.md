# sources/test-tools/fio/oslib/blkzoned.h

Purpose: declares fio's zoned block device OS abstraction and supplies stubs when native zoned-device support is unavailable.

Important APIs/functions: public functions cover zoned model discovery, zone reporting, write-pointer reset/move/finish, and max open/active zone limits. Under `CONFIG_HAS_BLKZONED`, implementations are external, normally `linux-blkzoned.c`. Without support, inline stubs return `-EIO` or `-ENODEV`, except block devices report `ZBD_NONE` to allow emulation.

Control flow and state: no persistent state in the header; behavior is compile-time selected.

Dependencies and integration: includes `zbd_types.h` and uses `struct thread_data`, `struct fio_file`, `struct zbd_zone`, and `enum zbd_zoned_model`. It integrates fio's generic ZBD logic with OS-specific Linux ioctls.

Risks: unsupported-platform stubs intentionally make most operations fail. The `blkzoned_get_max_active_zones()` stub parameter name is `max_open_zones`, a harmless but confusing mismatch.

Test signals: build both with and without `CONFIG_HAS_BLKZONED`; verify non-Linux behavior reports no native zones while Linux ZBD tests use real implementations.
