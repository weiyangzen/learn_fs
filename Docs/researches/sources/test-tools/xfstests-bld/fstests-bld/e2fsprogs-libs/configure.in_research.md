<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/configure.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/configure.in

## Purpose
This is the Autoconf input for the embedded e2fsprogs library tree used by xfstests-bld. It derives the e2fsprogs version/date from `version.h`, detects host/build capabilities, exposes many build toggles, and emits the configured `MCONFIG`, Makefiles, pkg-config files, headers, and RPM spec input needed to build e2fsprogs tools and libraries.

## Important APIs, Types, and Functions
The file is macro-driven rather than function-oriented. Key Autoconf interfaces include `AC_INIT`, `AC_PREREQ`, `AC_CANONICAL_HOST`, `AC_PROG_CC`, `AC_PROG_CPP`, `AC_CHECK_HEADERS`, `AC_CHECK_FUNCS`, `AC_CHECK_LIB`, `AC_SEARCH_LIBS`, `AC_CHECK_SIZEOF`, `AC_CHECK_DECL`, `AC_CHECK_TYPE`, `AC_SUBST`, `AC_SUBST_FILE`, and `AC_OUTPUT`. It also uses project macros such as `PKG_PROG_PKG_CONFIG`, `CHECK_GNU_MAKE`, `AX_TLS`, and `AM_GNU_GETTEXT`. Important substituted variables include `E2FSPROGS_VERSION`, `E2FSPROGS_PKGVER`, `LIB_EXT`, `LDFLAG_STATIC`, `LDFLAG_DYNAMIC`, `*_CMT` build comments, root install directories, `INTL_FLAGS`, `DO_TEST_SUITE`, and per-library dependency variables for uuid and blkid.

## Control Flow
The script first parses version metadata and normalizes release/package versions, including WIP/pre-release handling. It then sets toolchain defaults, processes legacy and current `--with`/`--enable` options, chooses static/shared/profile/checker library modes, and decides whether private or external `libuuid`/`libblkid` are used. Later phases probe programs, headers, functions, types, byte order, struct fields, socket/sem libraries, OS-specific defaults, static-link support, gettext setup, and cross-build behavior. The final phase creates build directories, builds an `outlist` only for outputs whose source directories exist, and calls `AC_OUTPUT($outlist)`.

## State and Persistence
The generated `configure` script persists build decisions in `config.status`, configured Makefiles, `MCONFIG`, `public_config.h`, `asm_types.h`, pkg-config files, and `e2fsprogs.spec`. It also creates build directories such as `lib`, `include`, `include/linux`, and `include/asm`. Runtime state is not stored here, but many compile-time defines such as `ENABLE_HTREE`, `CONFIG_TESTIO_DEBUG`, `CONFIG_BUILD_FINDFS`, `USE_UUIDD`, and `HAVE_EXT2_IOCTLS` shape compiled binaries.

## Dependencies and Integration Points
It integrates with e2fsprogs make fragments (`lib/Makefile.*`), gettext (`intl/Makefile`, `po/Makefile.in`, `libgnuintl.h`), type-generation helper `config/parse-types.sh`, Linux fallback headers under `include`, pkg-config for external uuid/blkid, and OS facilities such as `ldconfig`, `sem_init`, `socket`, `dlopen`, and ext2 ioctls. It directly controls whether downstream directories like `misc`, `e2fsck`, `debugfs`, `resize`, `doc`, and `intl` are included in the configured build.

## Risks
The template is legacy Autoconf syntax with many shell snippets, so quoting bugs can leak into generated configure behavior. Cross-compiling relies on a separate `BUILD_CC` and disables the test suite, which can hide target-only failures. The gettext section sets `VERSION="$E2FSPROGS_VERSION"` and then overwrites it with `VERSION=0.14.1`, a surprising compatibility artifact that can confuse package metadata readers. Feature toggles create many comment variables, so Makefile rules must keep using the matching `*_CMT` variables consistently. External `libuuid`/`libblkid` modes require working `pkg-config` and library probes.

## Test Signals
Useful validation signals are successful `autoconf` generation, `./configure` on Linux and at least one non-Linux host profile, `make`, `make check` when not cross-compiling, expected generated `MCONFIG` substitutions, correct `public_config.h`, correct selection of shared/static library extensions, and verifying that generated `e2fsprogs.spec` has the normalized package version.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/configure.in -->
