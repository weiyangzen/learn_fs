# File Research: sources/local-fs/xfsdump/librmt/rmtabort.c

Implements `_rmt_abort(fildes)`.

Behavior:
- Closes read and write pipe descriptors for a remote unit.
- Resets pipe slots to `-1`.
- Resets remote host type to `-1`.
- Emits a debug message if enabled.

Role:
- Central cleanup path after fatal remote protocol or pipe errors.
