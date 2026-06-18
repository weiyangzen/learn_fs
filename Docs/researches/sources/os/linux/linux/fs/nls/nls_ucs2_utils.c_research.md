# File Research: sources/os/linux/linux/fs/nls/nls_ucs2_utils.c

Purpose: Defines and exports compressed UCS-2 uppercase conversion tables shared by in-kernel Unicode/NLS users.

Core structures and data:
- `NlsUniUpperTable[512]` provides signed uppercase offsets for low Unicode code points.
- `UniCaseRangeU03a0`, `UniCaseRangeU0430`, `UniCaseRangeU0490`, `UniCaseRangeU1e00`, and `UniCaseRangeUff40` cover Greek, Cyrillic, extended Cyrillic, extended Latin/Greek, and fullwidth Latin ranges.
- `NlsUniUpperRange[]` lists those ranges and ends with a zeroed sentinel.

Important behavior:
- No conversion functions are defined here; inline logic lives in `nls_ucs2_utils.h`.
- `EXPORT_SYMBOL_GPL` exports the table and range list.
- Module metadata identifies this as `"NLS UCS-2"`.

Dependencies and interfaces:
- Includes `nls_ucs2_utils.h`.
- Code/data lineage comments reference CIFS Unicode support.

Design notes and risks:
- Signed offset encoding is compact but fragile because consumers add offsets directly to code points.
- Range boundaries and table lengths must stay synchronized with the sentinel-scanning logic.
