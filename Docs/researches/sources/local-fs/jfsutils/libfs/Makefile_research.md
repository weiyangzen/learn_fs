# File Research: sources/local-fs/jfsutils/libfs/Makefile

Configured Automake-generated Makefile for static internal library `libfs.a`.

Key contents:
- Builds `noinst_LIBRARIES = libfs.a`.
- Compiles many utility modules: filesystem subs, Unicode conversion, devices, util subs, superblock, inode, disk map, messages, endian, open-by-label, log dump/format/redo/work/read/map, and fsck message definitions.
- Include path is top-level `include`.
- Uses configured compiler/tools and concrete `/data2/jfsutils-1.1.15` paths.
- Creates archive with `ar cru` and `ranlib`.
- Dependency includes for all listed object files.

Interactions:
- `fscklog` links against this library.
- Other jfsutils programs likely share the same no-install archive.

Research notes:
- Configured generated file; `Makefile.am` is the concise source of library membership.
