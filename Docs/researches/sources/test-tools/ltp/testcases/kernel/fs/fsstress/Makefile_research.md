# sources/test-tools/ltp/testcases/kernel/fs/fsstress/Makefile

## Purpose

This Makefile builds the SGI-derived `fsstress` filesystem exerciser inside LTP with Linux-generic defaults.

## Important APIs, Types, and Functions

It sets `top_srcdir`, includes `env_pre.mk`, adds `CPPFLAGS += -DNO_XFS -I$(abs_srcdir) -D_LARGEFILE64_SOURCE -D_GNU_SOURCE`, suppresses `-Werror` via `CPPFLAGS += -Wno-error`, and includes `generic_leaf_target.mk`. The commented `LDLIBS += -lattr` documents the dependency if XFS support is re-enabled.

## Control Flow

The build imports the LTP environment prelude, applies compile flags, and delegates target generation to the generic leaf rules.

## State and Persistence Behavior

No runtime state is owned by the Makefile. The `-DNO_XFS` flag changes compiled behavior by selecting `xfscompat.h` and masking XFS-specific operation frequencies.

## Dependencies and Integration Points

Integrates `fsstress.c`, `global.h`, and `xfscompat.h` with the LTP build. It intentionally avoids requiring libxfs/libattr in the default build.

## Risks and Edge Cases

Removing `-DNO_XFS` requires restoring XFS headers and libattr linkage. `-Wno-error` acknowledges legacy warning noise, so compile warnings should not be mistaken for test correctness.

## Test Signals

The relevant signal is a successful build of `fsstress` under the default non-XFS configuration and, if changed, successful linkage against XFS/attr libraries.
