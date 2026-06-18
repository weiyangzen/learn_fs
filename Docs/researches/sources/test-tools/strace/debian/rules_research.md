# sources/test-tools/strace/debian/rules

## Purpose
Defines the Debian package build recipe for strace. It bootstraps autotools, configures normal, udeb, and selected 64-bit builds, applies Debian hardening/build flags, runs tests unless disabled, and drives debhelper install/package targets.

## Important APIs, Types, and Functions
Read coverage: 103 lines and 2494 bytes. Key make variables are `DEB_BUILD_MAINT_OPTIONS=hardening=+all`, `DPKG_EXPORT_BUILDFLAGS=1`, included `buildflags.mk` and `architecture.mk`, `CFLAGS`, `DEB_BUILD_OPTIONS`, `NUMJOBS`, `MAKEFLAGS`, `extra_build_targets`, `arch64_map`, `HOST64`, `CC64`, and `CONFIG_OPTS`. Targets include `all`, `build`, `build-arch`, `build-indep`, `configure`, pattern `%-stamp`, `build/Makefile`, `build-udeb/Makefile`, `build64/Makefile`, `clean`, `binary`, `binary-indep`, and `binary-arch`.

## Control Flow
The rules file enables hardening and dpkg build flags, adds `-Wall -g`, selects `-O0` for `noopt` or `-O2` otherwise, and honors `DEB_BUILD_OPTIONS=parallel=N`. It always adds a udeb build target and conditionally adds a 64-bit build for i386, powerpc, sparc, and s390 hosts. `CONFIG_OPTS` uses `--build` alone for native builds or adds `--host` for cross builds. The `configure` target runs `./bootstrap`. Each build directory is configured with `--enable-mpers=check --prefix=/usr`, with udeb disabling stacktrace/libiberty and build64 using `gcc -m64`.

The stamp rule builds the directory, runs `src/strace -V` and `make check VERBOSE=1` unless `nocheck` is set, then touches the stamp. `binary-arch` ensures build completion, renames the 64-bit binary/manpage to `strace64` when present, and runs debhelper commands from directory creation through builddeb. `clean` removes build directories and generated substvars before `dh_clean`.

## State and Persistence Behavior
Creates build directories `build`, `build-udeb`, and optionally `build64`, stamp files, generated configure outputs, test artifacts, binary/manpage rename artifacts for strace64, Debian substvars, and final package staging under `debian/`. Clean removes the main build artifacts and leaves source-controlled packaging files intact.

## Dependencies and Integration Points
Depends on GNU make, dpkg build flags and architecture makefiles, gcc, bootstrap/configure from this source tree, debhelper commands, and strace's test suite. It integrates with `configure.ac`, generated `debian/changelog`, Debian control/install/manpage files, udeb packaging for installer debugging, multiarch/biarch strace64 support, and Debian build option conventions.

## Risks and Edge Cases
Parallelism is manually translated into `MAKEFLAGS`; recursive make behavior should be checked. 64-bit companion builds only trigger for mapped 32-bit host architectures. Tests are skipped under `nocheck`, so package quality then depends on external CI. Renaming `strace` and `strace.1` in build64 must match install file expectations. Cross builds rely on `DEB_HOST_GNU_TYPE` and compiler availability. Udeb intentionally disables stacktrace and libiberty, so feature differences are expected.

## Test Signals
Run `debian/rules clean`, `build`, and `binary-arch` with and without `nocheck`, with `parallel=N`, and on mapped biarch hosts if available. Validate hardening flags, normal and udeb configure options, optional `strace64` artifacts, test execution through `src/strace -V` and `make check VERBOSE=1`, debhelper staging, and successful package lint/build parsing.
