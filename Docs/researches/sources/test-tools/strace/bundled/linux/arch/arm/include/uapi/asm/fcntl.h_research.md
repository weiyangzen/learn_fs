<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/arch/arm/include/uapi/asm/fcntl.h -->
# sources/test-tools/strace/bundled/linux/arch/arm/include/uapi/asm/fcntl.h

Purpose: ARM UAPI fcntl override header for open flags that differ from asm-generic defaults.

Important declarations: defines `O_DIRECTORY`, `O_NOFOLLOW`, `O_DIRECT`, and `O_LARGEFILE`, then includes `asm-generic/fcntl.h`.

Control flow: include guard plus preprocessor constants only.

State and persistence: compile-time ABI constants.

Dependencies and integration: used by strace bundled UAPI processing for ARM flag decoding.

Risks: small override files rely on generic fallback for all other definitions; if generic semantics change, ARM output changes too. Test signals: validate decoded ARM `open` flags against Linux UAPI and strace cross-architecture xlat generation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/arch/arm/include/uapi/asm/fcntl.h -->
