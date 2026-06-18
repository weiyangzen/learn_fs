# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfcid.c

Provides shared CID-keyed font dictionary utilities.

Key behavior:
- `cid_font_system_info_param` extracts and validates `CIDSystemInfo` from a CIDFont dictionary.
- `cid_font_data_param` extracts common CID font data including `CIDSystemInfo`, `CIDCount`, optional `GlyphDirectory`, and `GDBytes`.
- Requires `GDBytes` when no `GlyphDirectory` is present.
- Allows `GlyphDirectory` as a dictionary or array and treats `GDBytes` as optional in that case.

Dependencies:
- Uses CID font structures, dictionary parameter helpers, and shared font-building headers.

Research notes:
- This is helper code used by CID font builders; it centralizes validation of common CID dictionary fields.
