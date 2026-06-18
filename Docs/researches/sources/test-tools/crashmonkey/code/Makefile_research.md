# sources/test-tools/crashmonkey/code/Makefile

## Purpose

This Makefile builds the CrashMonkey kernel modules, C++ harness, user tools, test shared objects, generated ACE tests, sequence tests, and permuter plugins into `sources/test-tools/crashmonkey/build`. It also adapts some build flags and test inclusion rules to the running kernel version.

## Important APIs, Targets, and Variables

- `KERNEL_VERSION`, `KERNEL_MAJ`, and `KERNEL_MIN` derive version gates from `uname -r`.
- `MODULES = cow_brd disk_wrapper` and `obj-m` feed kbuild.
- `BUILD_DIR = $(CURDIR)/../build` isolates build products outside the source directory.
- `XATTR_DEF_FLAG` selects `-DNEW_XATTR_INC` for kernels 4.15 and newer.
- `FALLOC_ZERO_RANGE_TESTS` and `FALLOC_EXCLUDE` skip zero-range fallocate tests on kernels older than 3.15.
- `DELAY_DEFINE` selects harness timing macros (`THREE_THIRTEEN`, `FOUR_FOUR`, `FOUR_FIFTEEN`, `FOUR_SIXTEEN`, or `TWO_SEC`).
- High-level targets: `all`, `modules`, `c_harness`, `user_tools`, `tests`, `seq1`, `gentests`, `permuters`, and `clean`.
- Static pattern rules build generic_042 tests, seq1 generated tests, generated workloads, normal tests, permuter `.so` files, utility objects, and user tools.

## Control Flow

`all` builds kernel modules first, then the C++ harness, user tools, tests, seq1 workloads, and permuters. `modules` creates a build Makefile placeholder and delegates to the kernel build directory with `M=$(BUILD_DIR) src=$(CURDIR) modules`. C++ targets compile objects into mirrored build subdirectories and link tests as shared objects with `-shared -fPIC`. User tools link standalone executables against action and socket communication objects. `clean` delegates module cleanup to kbuild and removes selected testing binaries.

## State and Persistence Behavior

All normal build artifacts persist under `../build`: kernel module outputs, object files, shared-object tests, permuter plugins, user tool binaries, and `c_harness`. The source tree is read for tests via wildcard expansions, so generated `.cpp` files under `code/tests/seq1` or `code/tests/generated_workloads` automatically enter the build unless excluded.

## Dependencies and Integration Points

The Makefile depends on kernel headers at `/lib/modules/$(uname -r)/build`, GCC/G++, Linux kbuild, C++11, `dl`, and the CrashMonkey source layout. It consumes generated tests produced by ACE workload translators and builds them against `BaseTestCase`, `workload`, `actions`, `wrapper`, `DiskMod`, socket communication utilities, and result classes. Kernel module compilation consumes `cow_brd.c`, `disk_wrapper.c`, `bio_alias.h`, and ioctl headers.

## Risks and Edge Cases

- Kernel version gates are narrow and manually curated; unsupported versions can fail either in `bio_alias.h` or during kbuild.
- `DELAY_DEFINE` defaults to `TWO_SEC` when `CM` is unset, which can hide timing assumptions in harness behavior.
- Several object pattern rules use broad `%.cpp` prerequisites, so current-directory assumptions matter.
- Generated source files can unexpectedly enter `seq1` or `gentests` targets due to wildcard discovery.
- `clean` only removes module build outputs and a few binaries; many C++ build artifacts under `../build` may remain.
- Xattr include flags are based on running kernel version, not necessarily the target headers if cross-building.

## Test Signals

Core signals are successful `make modules`, `make c_harness`, `make user_tools`, `make tests`, `make seq1`, and `make permuters` on supported kernel versions. Generated workload signals include a new `.cpp` file appearing in the expected test directory and a corresponding `.so` under `../build`. Negative build tests should cover old kernels for fallocate-zero exclusion and unsupported kernels for expected `bio_alias.h` failure.
