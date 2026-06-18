# sources/test-tools/iozone/src/current/makefile

Purpose: platform matrix makefile for building iozone, `fileop`, and `pit_server` across legacy Unix, Linux, BSD, Solaris, Windows/Cygwin/SUA, and other targets. The default `all` target prints supported explicit targets rather than building.

Important APIs/types/functions: make variables include `CC`, `C89`, `GCC`, `CCS`, `NACC`, `CFLAGS`, `LDFLAGS`, `S10GCCFLAGS`, `S10CCFLAGS`, and `FLAG64BIT`. User-facing targets include `linux`, `linux-AMD64`, `linux-arm`, `linux-powerpc*`, `linux-S390*`, `Solaris*`, `AIX*`, `freebsd`, `openbsd`, `macosx`, `Windows`, `SUA`, `clean`, `rpm`, and `pantheon`. Object rules compile `iozone.c`, `libasync.c`, `libbif.c`, `fileop.c`, and `pit_server.c` with per-platform macro sets such as `ASYNC_IO`, `NO_THREADS`, `SHARED_MEM`, `_LARGEFILE64_SOURCE`, `_FILE_OFFSET_BITS=64`, `HAVE_PREAD`, `DONT_HAVE_O_DIRECT`, and platform `NAME` strings.

Control flow: each platform target depends on a set of object files, then links the needed binaries with platform-specific libraries. Object rules echo the build target, compile iozone and support libraries with the relevant macros, and reuse common output names like `libasync.o` and `libbif.o`. Targets that support `fileop` and `pit_server` build those additional binaries. `clean` removes object files and three binaries; `rpm` copies source tarballs into RPM build dirs and runs `rpmbuild -ba spec.in`.

State/persistence behavior: builds write object files and binaries directly into `src/current`; many targets share object names, so switching targets without `make clean` can mix incompatible objects. The `rpm` target writes to `/usr/src/red*/SO*` and invokes system RPM build state.

Dependencies/integration: tightly coupled to `iozone.c`, `libasync.c`, `libbif.c`, `fileop.c`, `pit_server.c`, and RPM `spec.in`. Platform link dependencies include pthreads, realtime/AIO libraries, Solaris networking libraries, HP/AIX/SCO specialty libraries, and optional VXFS headers. Downstream packaging and CI likely select architecture-specific targets rather than the default.

Risks/test signals: the file encodes many legacy targets with repeated commands, duplicated compile lines, target-specific object reuse, and some apparent copy/paste defects; broad compile coverage is the main safety net. Linux smoke tests should run `make clean && make linux` or `linux-AMD64`, then execute `iozone`, `fileop`, and `pit_server` basics. Cross-target tests should always clean first to avoid stale objects.
