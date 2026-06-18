# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfcmap.h

This header defines Ghostscript's internal, representation-neutral CMap structures. CMaps map variable-length input character codes to font-specific glyph spaces such as CIDs. The file notes it would be named `gxcmap.h`, but that name is already used.

The code-space model uses sorted, non-overlapping `gx_code_space_range_t` ranges with 1 to 4 bytes (`MAX_CMAP_CODE_SIZE`). Lookup entries can represent single keys or key ranges and map to CIDs, glyphs, character strings, or notdef CIDs. `CODE_VALUE_CID` range entries increment results by input-code offset, while `CODE_VALUE_NOTDEF` does not.

`GS_CMAP_COMMON` defines shared CMap fields: `CMapType`, internal id, name, per-font CIDSystemInfo array, font count, version, UID/XUID, UIDOffset, writing mode, Unicode/ToUnicode flags, glyph-name callback/data, and a `gs_cmap_procs_t` virtual procedure table.

`gs_cmap_procs_t` abstracts decoding, code-space enumeration, lookup enumeration, and identity checking so Adobe CMaps and TrueType cmap-backed implementations can share the same higher-level interface.

The header defines enumeration state for code-space ranges and lookup tables. Range enumeration returns one `gx_code_space_range_t` at a time. Lookup enumeration separates lookup-level metadata (`key_size`, range flag, value type, font index) from entry-level key/value data, and may use temporary storage for values that do not survive across calls.

Client procedures initialize and advance range/lookup enumerators. Implementation procedures initialize common CMap fields, allocate a CMap, set up enumerators, check identity using fast paths, and compute identity generically.

Filesystem relevance: none. It is font/text mapping infrastructure.
