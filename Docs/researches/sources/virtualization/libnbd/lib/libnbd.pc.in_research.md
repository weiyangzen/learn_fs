# File Research: sources/virtualization/libnbd/lib/libnbd.pc.in

Installed pkg-config template for libnbd.

Content:
- Uses configured prefix, exec_prefix, libdir, and includedir.
- Exposes package name, version, description.
- Leaves `Requires` and `Cflags` empty.
- Emits `Libs: -lnbd`.

Research notes:
- Because no `-L${libdir}` or include path is emitted here, consumers rely on pkg-config installation context/default paths or compiler/linker defaults.
