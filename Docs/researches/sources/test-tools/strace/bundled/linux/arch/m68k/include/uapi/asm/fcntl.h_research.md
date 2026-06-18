<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/arch/m68k/include/uapi/asm/fcntl.h -->
# sources/test-tools/strace/bundled/linux/arch/m68k/include/uapi/asm/fcntl.h

Purpose: m68k UAPI fcntl override header for architecture-specific open flag values.

Important declarations: defines `O_DIRECTORY`, `O_NOFOLLOW`, `O_DIRECT`, and `O_LARGEFILE`, then includes `asm-generic/fcntl.h`.

Control flow: include guard and macro definitions only.

State and persistence: compile-time constants.

Dependencies and integration: used by strace bundled header extraction for m68k personalities.

Risks: minimal override pattern depends on generic header for all remaining fcntl commands and structs. Test signals: cross-check generated m68k xlat values with Linux UAPI.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/arch/m68k/include/uapi/asm/fcntl.h -->
