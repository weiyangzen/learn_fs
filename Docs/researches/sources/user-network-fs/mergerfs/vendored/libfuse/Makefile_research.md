<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/Makefile -->
# sources/user-network-fs/mergerfs/vendored/libfuse/Makefile

Purpose: This Makefile builds the vendored mergerfs-flavored libfuse static library and Linux-only helper utilities. The primary output is `build/libfuse.a`, with optional `build/mergerfs-fusermount` and `build/mount.mergerfs`.

Important controls: variables expose tool overrides (`AR`, `INSTALL`, `STRIP`, etc.), build mode flags (`RELEASE`, `SANITIZE`, `LTO`, `STATIC`), standard GNU install directories, and `FUSERMOUNT_DIR`. `SRC_CXX` is all `lib/*.cpp`; object and dependency files live under `build/.objs`. Compilation uses `_FILE_OFFSET_BITS=64`, C++20, GNU99 for C sources, dependency generation, `-D_REENTRANT`, and include paths for `include`, `..`, and `build`.

Control flow and persistence: `all` builds `libfuse.a` and, on Linux, utilities. `build/stamp` creates the build tree. Pattern rules compile C/C++ sources, `ar rcs` archives the library, `strip` mutates utility binaries, `clean` deletes the build directory, and `install-utils` installs utilities and marks `mergerfs-fusermount` setuid root.

Risks and test signals: install behavior is privileged and security-sensitive because of setuid. `LDLIBS` is defined but not used in the `mount.mergerfs` link line, so link failures can reveal missing pthread/rt/atomic needs depending on toolchain. Tests should run `make clean all`, release/sanitize variants, non-Linux utility suppression, and packaging install into a `DESTDIR`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/Makefile -->
