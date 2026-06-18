# File Research: sources/virtualization/qemu/block/export/meson.build

Build manifest for block export sources. It always adds `export.c`, conditionally adds `vhost-user-blk-server.c` and `virtio-blk-handler.c` when vhost-user block server support is enabled, conditionally adds `fuse.c` when FUSE support is available, and conditionally adds VDUSE export sources plus `libvduse`.
