# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/hvm/save.h

Imported Xen public HVM save/restore record framework.

Purpose:
- Defines generic HVM migration/save-state record descriptors and type macros, then includes architecture-specific HVM save records.

Key content:
- Documents strict 32/64-bit layout requirements: explicit sizes, natural alignment, and multiples of 8 bytes.
- Requires GNU anonymous structs/unions.
- Defines `struct hvm_save_descriptor` with typecode, instance, and payload length.
- Defines `DECLARE_HVM_SAVE_TYPE*` machinery and `HVM_SAVE_TYPE`, `HVM_SAVE_LENGTH`, `HVM_SAVE_CODE`.
- Defines terminator record `hvm_save_end`.
- Includes x86 or ARM architecture-specific HVM save header based on target architecture.

Integration:
- Used by `domctl.h` HVM context operations.
- Not used by the visible 9front PV guest runtime.

Risks/notes:
- Save/restore ABI is highly layout-sensitive.
- Requires architecture-specific companion headers to be present and compatible.
