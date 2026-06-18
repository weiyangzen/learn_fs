# File Research: sources/virtualization/spdk/module/fsdev/aio/aio_mgr.h

Declares the AIO manager abstraction for fsdev AIO.

Key elements:
- Forward declares `spdk_aio_mgr` and `spdk_aio_mgr_io`.
- Defines `fsdev_aio_done_cb`.
- Declares create, read, write, cancel, poll, and delete functions.

Dependencies:
- Includes SPDK stdinc and queue headers for shared types.

Research notes:
- Both POSIX AIO and Linux libaio implementations satisfy this interface.
