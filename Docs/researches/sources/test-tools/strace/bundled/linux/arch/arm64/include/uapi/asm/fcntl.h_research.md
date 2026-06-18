<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/arch/arm64/include/uapi/asm/fcntl.h -->
# sources/test-tools/strace/bundled/linux/arch/arm64/include/uapi/asm/fcntl.h

Purpose: ARM64 UAPI fcntl header, primarily preserving AArch32 compatibility flag values.

Important declarations: defines `O_DIRECTORY`, `O_NOFOLLOW`, `O_DIRECT`, and `O_LARGEFILE`; comments note these are custom definitions for AArch32 compat support. Includes `asm-generic/fcntl.h`.

Control flow: include guard and preprocessor definitions.

State and persistence: compile-time constants only.

Dependencies and integration: supports strace decoding for arm64 and compat personalities.

Risks: compat-specific values must remain synchronized with kernel headers or strace can mislabel flags for 32-bit tasks on arm64. Test signals: compare generated constants for both native arm64 and AArch32 compat runs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/arch/arm64/include/uapi/asm/fcntl.h -->
