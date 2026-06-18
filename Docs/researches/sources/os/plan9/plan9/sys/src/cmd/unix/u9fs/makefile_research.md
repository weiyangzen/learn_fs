# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/makefile

- Role: Unix makefile for building the `u9fs` executable.
- Build inputs: Compiles authentication modules, 9P conversion modules, DES, formatting, UTF, utility, and `u9fs.o`.
- Configuration: Notes platform-specific SGI/SunOS flags, optional `inttypes.h` replacement, and socket/nsl linker additions.
- Targets: `u9fs`, pattern `.c.o`, `clean`, and `install`.
- Risks/notes: Header dependency list omits some included headers such as `oldfcall.h`/`u9fs.h`, so incremental rebuilds may be incomplete.
