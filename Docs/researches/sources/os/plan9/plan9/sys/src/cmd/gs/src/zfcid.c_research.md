# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfcid.c

Provides shared CID-keyed font utility routines.

`cid_font_system_info_param()` retrieves `CIDSystemInfo` from a CID font dictionary and parses it with `cid_system_info_param()`.

`cid_font_data_param()` validates a CID font dictionary and fills `gs_font_cid_data` with `CIDSystemInfo`, `CIDCount`, and `GDBytes` handling. It also returns the `GlyphDirectory` reference when present.

If `GlyphDirectory` is absent, `GDBytes` is required for standard CIDFont data. If `GlyphDirectory` is present as a dictionary or array, `GDBytes` is optional because the client may still need it for `CIDMap`.

The file has no operator table; it exports utilities used by CID font builders.
