# File Research: sources/local-fs/linux-apfs-rw/Makefile

This is the out-of-tree Linux kernel module build file for the APFS driver. It builds one module, `apfs.o`, using kbuild with `obj-m = apfs.o`.

The module object list is explicit in `apfs-y`: APFS core sources such as `btree.o`, `compress.o`, `dir.o`, `extents.o`, `file.o`, `inode.o`, `node.o`, `object.o`, `spaceman.o`, `super.o`, `transaction.o`, `xattr.o`, and bundled LZFSE/LZVN decoder objects.

Build variables default to the running kernel: `KERNELRELEASE ?= $(shell uname -r)`, `KERNEL_DIR ?= /lib/modules/$(KERNELRELEASE)/build`, and `PWD := $(shell pwd)`.

`ccflags-y += $(APFS_CONFIG)` allows optional compile-time flags. The file documents `APFS_CONFIG=-DCONFIG_APFS_RW_ALWAYS`, which makes mounts writable by default and is explicitly marked risky.

Targets:
- `default`: runs `./genver.sh`, then invokes `make -C $(KERNEL_DIR) M=$(PWD)`.
- `install`: runs kbuild `modules_install`.
- `clean`: removes generated `version.h`, then runs kbuild clean.

Research relevance: this file defines the module composition and the feature flag entry point for default read-write behavior.
