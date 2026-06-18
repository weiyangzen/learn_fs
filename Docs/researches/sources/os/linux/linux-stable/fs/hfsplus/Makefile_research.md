# File Research: sources/os/linux/linux-stable/fs/hfsplus/Makefile

## Scope

Builds the HFS+ module/object and optional HFS+ KUnit test object.

## Build Composition

`hfsplus.o` is composed from superblock/options/inode/ioctl/extents/catalog/dir/B-tree/unicode/wrapper/bitmap/partition/attribute/xattr sources. `unicode_test.o` is built when `CONFIG_HFSPLUS_KUNIT_TEST` is enabled.

## Dependencies And Risks

The object list shows the runtime subsystem boundaries: B-trees, catalog, allocation/extents, Unicode conversion, wrapper/partition probing, inode/superblock integration, and xattr families. Build failures in any listed component block the single `hfsplus` filesystem object.
