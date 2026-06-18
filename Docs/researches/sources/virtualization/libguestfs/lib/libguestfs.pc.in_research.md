# File Research: sources/virtualization/libguestfs/lib/libguestfs.pc.in

Installed pkg-config template for libguestfs.

Important behavior:
- Defines configured `prefix`, `exec_prefix`, `libdir`, and `includedir`.
- Exposes package name, version, and description.
- Leaves `Requires` and `Cflags` empty.
- Provides `Libs: -lguestfs`.

Filesystem relevance:
- Build integration metadata for clients linking against libguestfs filesystem/image access APIs.
