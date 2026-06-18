# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/Makefile.in

Purpose: autoconf make template for building, testing, installing, and cleaning e2fsprogs `libblkid`.

Important build APIs and control flow: defines object/source lists for cache, device, probe, read, resolve, save, topology, tag, version, size, and seek units. Includes generated e2fsprogs make fragments for static, ELF, BSD, profile, and checker libraries. Builds generated headers `blkid_types.h` via `config.status` and copies `blkid.h.in` to `blkid.h`. Produces `libblkid.3`, `blkid.pc`, optional test executables, and a standalone `blkid` utility linked with `libuuid`.

State and persistence: generated artifacts include headers, man page, pkg-config file, libraries, object directories, and test scripts. Install targets write headers under `$(includedir)/blkid`, library under `$(libdir)`, and pkg-config metadata.

Dependencies and integration: depends on top-level `MCONFIG`, uuid library, substitution tools, and e2fsprogs build macros.

Risks and test signals: generated header/config substitutions must match compiler ABI. Test `make all`, `make check`, install/uninstall, clean/distclean, shared/static variants, and dependency regeneration.
