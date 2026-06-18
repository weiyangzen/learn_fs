<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/test/Makefile -->
# sources/test-tools/strace/attic/test/Makefile

Purpose: simple historical makefile for compiling attic strace regression/reproducer programs.

Important declarations: `CFLAGS += -Wall`; `PROGS` lists signal, clone, thread, ioctl, seccomp, mmap, and x32 reproducers. `leaderkill` and `childthread` add `-pthread` via target-specific `LDFLAGS`. `clean distclean` removes objects, cores, programs, and `*.gdb`.

Control flow: default `all` builds all programs through make's implicit C rules.

State and persistence: creates local binaries and object files; cleanup removes them.

Dependencies and integration: depends on system C compiler, Linux headers, pthreads, and architecture-specific support for some programs.

Risks: no per-program feature detection, so unsupported headers/syscalls break full `make`. As attic content, it is unlikely to be part of current CI. Test signals: run `make -k` to identify portable versus host-specific reproducers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/test/Makefile -->
