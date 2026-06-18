# File Research: sources/os/linux/linux/fs/isofs/Makefile

Builds the ISO9660 filesystem module/object.

Objects:
- Core `isofs-y`: `namei.o inode.o dir.o util.o rock.o export.o`
- Optional Joliet: `joliet.o`
- Optional zisofs decompression: `compress.o`

The aggregate object is built when `CONFIG_ISO9660_FS` is enabled.
