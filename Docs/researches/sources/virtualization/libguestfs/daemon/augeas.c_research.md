# File Research: sources/virtualization/libguestfs/daemon/augeas.c

Provides the daemon’s Augeas API implementation with one process-global Augeas handle.

Key points:
- Maintains static `augeas *aug`; callers must initialize via `do_aug_init`.
- `aug_read_version` lazily opens a no-load Augeas handle and encodes version as `(major << 16) | (minor << 8) | patch`.
- Destructor `aug_finalize` closes any live handle.
- Implements wrappers for `aug_defvar`, `aug_defnode`, `aug_get`, `aug_set`, `aug_clear`, `aug_insert`, `aug_rm`, `aug_mv`, `aug_match`, `aug_save`, `aug_load`, `aug_ls`, `aug_setm`, `aug_label`, and `aug_transform`.
- Converts Augeas internal strings into caller-owned copies.
- Errors include detailed Augeas message/minor/details through `AUGEAS_ERROR` or local error formatting.
