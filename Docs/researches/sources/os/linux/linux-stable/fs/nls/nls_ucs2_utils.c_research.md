# File Research: sources/os/linux/linux-stable/fs/nls/nls_ucs2_utils.c

Purpose: Defines and exports compressed UCS-2 uppercase conversion tables shared by in-kernel Unicode/NLS users.

Core structures and data:
- `NlsUniUpperTable[512]` provides signed offsets for low Unicode code points, especially ASCII/Latin ranges.
- `UniCaseRangeU03a0`, `UniCaseRangeU0430`, `UniCaseRangeU0490`, `UniCaseRangeU1e00`, and `UniCaseRangeUff40` hold signed offsets for Greek, Cyrillic, extended Cyrillic, extended Latin/Greek, and fullwidth Latin.
- `NlsUniUpperRange[]` lists those ranges and terminates with a zeroed sentinel.

Important behavior:
- There are no conversion functions in this C file; logic lives in `nls_ucs2_utils.h`.
- The tables are exported with `EXPORT_SYMBOL_GPL` for use by other GPL-compatible kernel code.
- Module metadata identifies this as `"NLS UCS-2"` with GPL license.

Dependencies and interfaces:
- Includes `nls_ucs2_utils.h`, which in turn uses the declarations from `nls_ucs2_data.h`.
- Origin comments indicate code/data lineage from CIFS Unicode support.

Design notes and risks:
- The signed offset encoding is compact but fragile: consumers add the signed offset to the input code point.
- Range boundaries and table lengths must stay synchronized; the sentinel is how `UniToupper()` knows to stop.
