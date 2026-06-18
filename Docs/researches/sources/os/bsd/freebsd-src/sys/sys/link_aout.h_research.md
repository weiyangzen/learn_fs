# File Research: sources/os/bsd/freebsd-src/sys/sys/link_aout.h

Defines legacy a.out runtime linker and shared-library structures, compatible with SunOS-style shared library schemes. It includes shared object descriptors (`sod`), runtime shared object maps (`so_map`), symbol-with-size entries (`nzlist`), section dispatch tables, RRS hash buckets, runtime symbols, and debugger interface state.

`struct _dynamic` describes the dynamic-linking interface, with version constants for Sun and BSD formats and macros to access GOT, PLT, relocation, symbol, hash, string, needed-object, and path sections plus their sizes.

It also defines ld.so entry points (`ld_entry`), crt0-to-rtld handoff (`crt_ldso`) and versions, hints-file header/bucket formats, maximum Dewey version components, bad-magic check, and the legacy hints path `/var/run/ld.so.hints`.
