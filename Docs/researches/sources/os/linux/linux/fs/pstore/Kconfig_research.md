# File Research: sources/os/linux/linux/fs/pstore/Kconfig

## Role

Defines configuration options for the Linux persistent storage subsystem and its RAM/block frontends.

## Options

- `PSTORE`: core persistent store filesystem and platform backend support.
- `PSTORE_DEFAULT_KMSG_BYTES`: default kernel log snapshot size.
- `PSTORE_COMPRESS`: zlib deflate compression for dmesg records.
- `PSTORE_CONSOLE`: persistent console logging.
- `PSTORE_PMSG`: `/dev/pmsg0` userspace persistent message logging.
- `PSTORE_FTRACE`: persistent ftrace function-call tracing.
- `PSTORE_RAM`: ramoops RAM backend with Reed-Solomon ECC support.
- `PSTORE_ZONE`: common zone manager used by pstore/blk.
- `PSTORE_BLK`: block-device-backed pstore.
- `PSTORE_BLK_BLKDEV`: block device selector string.
- `PSTORE_BLK_KMSG_SIZE`, `PSTORE_BLK_MAX_REASON`, `PSTORE_BLK_PMSG_SIZE`, `PSTORE_BLK_CONSOLE_SIZE`, `PSTORE_BLK_FTRACE_SIZE`: block backend sizing and kmsg reason limits.

## Research Notes

The configuration separates frontends from backends. `PSTORE` supplies the common filesystem/platform layer, while RAM and block storage select the lower-level support they require.
