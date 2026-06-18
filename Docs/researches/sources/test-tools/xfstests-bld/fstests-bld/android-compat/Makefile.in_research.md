# sources/test-tools/xfstests-bld/fstests-bld/android-compat/Makefile.in

Purpose: Autoconf template for building Android compatibility static/shared libraries and headers needed when cross-compiling xfstests components for bionic.

Important APIs and functions: variables for tool substitutions, `OBJS_RT`, `OBJS_COMPAT`, `LIBS`, `INCLUDES`, `SYS_INCLUDES`; targets `all`, `librt.a`, `libandroid_compat.a`, `libpthread.a`, `aio.h`, `install`, `clean`, and regenerated `Makefile`.

Control flow: compiles each C source into normal and `elfshared` PIC objects. Builds a stub `librt`, empty `libpthread`, and `libandroid_compat`; installs libraries and headers into configured prefix paths.

State and persistence: produces `.o`, `.a`, `.so.1.0`, `aio.h`, and `elfshared` artifacts; install persists libraries and headers into `libdir` and `includedir`.

Dependencies and integration: configured by `configure`; invoked by `build-all` in Android cross builds. Consumed by xfsprogs/xfstests builds via `-landroid_compat`.

Risks: `libandroid_compat.so.1.0` links `$(OBJS_RT)` instead of `$(OBJS_COMPAT)`, which appears suspicious. The empty `libpthread.a` may satisfy linkers but not functionality.

Test signals: successful `./configure && make && make install` under Android cross toolchain.
