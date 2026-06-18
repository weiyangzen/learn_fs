# File Research: sources/os/linux/linux-stable/fs/isofs/Makefile

Builds the ISOFS module/object.

Composition:
- `obj-$(CONFIG_ISO9660_FS) += isofs.o`
- Base object list: `namei.o inode.o dir.o util.o rock.o export.o`
- Optional Joliet support adds `joliet.o`
- Optional zisofs compression support adds `compress.o`
