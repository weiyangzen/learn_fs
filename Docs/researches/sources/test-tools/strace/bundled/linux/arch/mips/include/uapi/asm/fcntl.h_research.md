<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/arch/mips/include/uapi/asm/fcntl.h -->
# sources/test-tools/strace/bundled/linux/arch/mips/include/uapi/asm/fcntl.h

Purpose: MIPS UAPI fcntl header defining MIPS-specific open flags, fcntl commands, and flock padding.

Important declarations: includes `<asm/sgidefs.h>`, defines hex values for `O_APPEND`, `O_DSYNC`, `O_NONBLOCK`, create/truncate/exclusive/noctty, `FASYNC`, `O_LARGEFILE`, `__O_SYNC`/`O_SYNC`, `O_DIRECT`, lock commands, owner commands, 64-bit lock commands for 32-bit/kernel builds, and ABI-dependent `__ARCH_FLOCK_EXTRA_SYSID`/`__ARCH_FLOCK_PAD` when not ABI64. Includes generic fcntl afterward.

Control flow: preprocessor conditionals on `__BITS_PER_LONG`, `__KERNEL__`, and `_MIPS_SIM`.

State and persistence: compile-time ABI constants and struct padding macros.

Dependencies and integration: critical for strace MIPS fcntl/open decoding and flock structure layout.

Risks: MIPS ABI conditionals are easy to mis-evaluate in generator environments. Wrong `_MIPS_SIM` values can produce incorrect struct layouts. Test signals: build generated xlats for o32/n32/n64 and compare decoded flags/locks against kernel UAPI.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/arch/mips/include/uapi/asm/fcntl.h -->
