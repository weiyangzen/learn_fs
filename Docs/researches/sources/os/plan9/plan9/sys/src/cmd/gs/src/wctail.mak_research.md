# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/wctail.mak

Tail fragment common to Watcom makefiles.

Key points:
- Includes `version.mak`, core `gs.mak`, `lib.mak`, JPEG, zlib, libpng, JBIG2, icclib, and ijs make fragments.
- Defines auxiliary tool build/link rules for `echogs`, `genarch`, `genconf`, `gendev`, and `geninit`.
- Uses temporary response file `_temp_.tr` for Watcom linker options, stubs, stacks, and library paths.
- Generates blank `gconfig_.h`.
- Generates `gconfigv.h` with `USE_ASM`, `USE_FPU`, `EXTEND_NAMES`, and `SYSTEM_CONSTANTS_ARE_WRITABLE`.

Dependencies and interactions:
- Complements `wccommon.mak`.
- Used before DOS/Watcom-specific device and platform rules.

Research relevance:
- Provides common generated-tool and generated-config behavior for Watcom builds.
