# File Research: sources/os/bsd/freebsd-src/sys/sys/linker.h

Defines FreeBSD kernel linker and KLD user/kernel ABI interfaces.

Key content:
- Kernel-only `struct linker_file`, `struct linker_class`, symbol typedefs, and callbacks for loaded ELF objects.
- Tracks module reference counts, pathname, load address/size, constructors/destructors, dependency files, common symbols, contained modules, preload dependency state, and tracing metadata.
- Declares kernel linker APIs: module reference/release, loaded-file iteration, symbol lookup, linker set lookup, function enumeration, file unload, dependency loading, DDB symbol helpers, HWPMC object listing, and kldload busy/unbusy coordination.
- Defines boot/preload metadata constants such as `MODINFO_*` and `MODINFOMD_*`, plus preload search/fetch APIs.
- Declares ELF relocation and CTF support hooks used by linker backends.
- Exposes user-visible KLD syscall structures: `struct kld_file_stat`, `struct kld_sym_lookup`, unload flags, and libc prototypes for `kldload`, `kldunload`, `kldfind`, `kldstat`, `kldsym`, etc.

Research relevance:
- This is the central interface between boot-loaded modules, runtime-loaded KLDs, module metadata, and kernel symbol/relocation services.
- It is tightly coupled with `module.h` and `linker_set.h`: module metadata is collected through linker sets and interpreted by the runtime linker/module subsystem.
- Filesystem and storage modules depend on this ABI for load/unload, version/dependency checks, exported symbol resolution, and static constructor/destructor handling.

Cautions:
- Several definitions are kernel-only, while KLD syscall ABI structs are shared with userland.
- `MODINFOMD_*` values have machine-dependent caveats, especially PowerPC.
- `struct kld_file_stat_1` is legacy and versioned by struct size.
