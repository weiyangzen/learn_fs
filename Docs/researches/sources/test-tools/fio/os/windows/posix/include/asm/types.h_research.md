# sources/test-tools/fio/os/windows/posix/include/asm/types.h

Purpose: tiny Linux compatibility header for code that expects `<asm/types.h>` integer aliases.

Important APIs/types: defines `__u16`, `__u32`, and `__u64` as unsigned 16/32/64-bit-like C integer aliases.

Control flow and state: no logic or state; compile-time type compatibility only.

Dependencies and integration: supports fio code and imported Linux-style headers that use `__u*` names on Windows.

Risks: it does not define signed aliases or the full Linux UAPI type set. Exact widths rely on Windows compiler assumptions for `unsigned short`, `unsigned int`, and `unsigned long long`.

Test signals: Windows compilation of any Linux-UAPI-like structures using these aliases.
