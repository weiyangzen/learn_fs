<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/arch/powerpc/include/uapi/asm/fcntl.h -->
# sources/test-tools/strace/bundled/linux/arch/powerpc/include/uapi/asm/fcntl.h

Purpose: PowerPC UAPI fcntl override header for selected open flag values.

Important declarations: defines `O_DIRECTORY`, `O_NOFOLLOW`, `O_LARGEFILE`, and `O_DIRECT`, then includes `asm-generic/fcntl.h`.

Control flow: include guard and preprocessor constants only.

State and persistence: compile-time ABI constants.

Dependencies and integration: supports strace decoding for PowerPC personalities.

Risks: generic fallback fills most fcntl definitions, so subtle PowerPC differences must be captured in this override list. Test signals: compare generated PowerPC open flag xlats with upstream Linux headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/arch/powerpc/include/uapi/asm/fcntl.h -->
