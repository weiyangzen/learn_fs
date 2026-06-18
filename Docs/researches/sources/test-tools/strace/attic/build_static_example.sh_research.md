<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/build_static_example.sh -->
# sources/test-tools/strace/attic/build_static_example.sh

Purpose: historical shell example for building a small statically linked strace binary with size-oriented compiler and linker flags.

Important commands: sets `CC` to `x86_64-gcc`, builds `CFLAGS` with `-Os`, `-static`, section splitting, alignment minimization, unwind table suppression, linker garbage collection, and map file generation. Then runs `./bootstrap`, `./configure $BUILDFLAG`, and `make CC="$CC" CFLAGS="$CFLAGS"`.

Control flow: straight-line `sh -e` script; commented alternatives mention i686 builds and stack boundary tuning.

State and persistence: generates Autotools files, configured build state, binaries, object files, and `strace.mapfile`.

Dependencies and integration: depends on static-capable compiler/libc, Autotools, and strace's bootstrap/configure system.

Risks: static linking may fail on modern distributions without static libraries. Aggressive alignment and stack comments are architecture/compiler sensitive. Script is in `attic`, so it likely is not CI-covered. Test signals: successful static `make`, inspect `file strace`, run `size strace`, and smoke-test `./strace true`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/build_static_example.sh -->
