# sources/user-network-fs/rclone/librclone/ctest/Makefile

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/ctest/Makefile -->
## sources/user-network-fs/rclone/librclone/ctest/Makefile

Purpose: builds and runs the C demonstration/test program for `librclone`'s C archive interface.

Important APIs and control flow: platform conditionals set executable suffix, library name (`librclone.lib` on Windows, `librclone.a` otherwise), and linker flags. `ctest` links `ctest.o` with the generated library. `ctest.o` compiles `ctest.c` and generated `librclone.h`. The library/header rule runs `go build --buildmode=c-archive -o $(LIB) github.com/rclone/rclone/librclone`. `test` runs the executable. `clean` removes build artifacts.

State, dependencies, and integration: integrates Go's c-archive output with a C compiler. It assumes `go`, `CC`, platform link libraries, and the generated header are available.

Risks and test signals: `ctest.o` compiles both `ctest.c` and `librclone.h` with `-c $^`, which may create header precompiled artifacts depending on compiler behavior. The Makefile is a smoke/demo build path rather than production packaging.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/ctest/Makefile -->
