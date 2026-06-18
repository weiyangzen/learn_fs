<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/Makefile -->
# sources/user-network-fs/mergerfs/Makefile

## Purpose

This is the top-level mergerfs build, package, install, and release makefile. It compiles all `src/*.cpp` into `build/mergerfs`, links companion tool symlinks, drives tests, builds vendored libfuse, installs binaries/manpages/preload library, generates changelogs/version headers, and delegates Debian/RPM/container release builds. The source was read as a complete 409-line file (11045 bytes).

## Important APIs, Types, and Functions

make targets: `BUILDDIR`, `DEFAULT_TARGET`, `OPT_FLAGS`, `STATIC_FLAGS`, `LTO_FLAGS`, `SRC`, `OBJS`, `DEPS`, `TESTS`, `TESTS_OBJS`, `TESTS_DEPS`, `MANPAGE`, `override INC_FLAGS`, `override MFS_FLAGS`, `override TESTS_FLAGS`, `LIBFUSE`, `LDLIBS`, `.PHONY`, and 41 more

## Control Flow

Make control flow starts at `all`, builds vendored libfuse, compiles dependency-tracked objects into `build/.objs`, links `mergerfs`, creates symlink tools, and branches into install, package, tarball, release, and container targets. Release targets call `buildtools/build-release` with target-specific arguments.

## State and Persistence Behavior

Persistent effects are build artifacts, packages, generated version/changelog files, container images, mounted test images, or published documentation. Most state is external to the script: git refs, package-manager caches, podman images, and output directories.

## Dependencies and Integration Points

external tools: `fakeroot`, `git`, `rpmbuild`, `make`, `mount`, `dpkg-buildpackage`

## Risks and Edge Cases

Release and install targets mutate the working tree (`VERSION`, `src/version.hpp`, changelogs), shell out to distro packaging tools, and run clean/distclean. Quoting and environment overrides must be preserved for packaging reproducibility.

## Test Signals

`make all`, `make tests`, `make install DESTDIR=...`, `make deb`, `make rpm` on supported distros, and release-target dry runs with a temporary package directory.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/Makefile -->
