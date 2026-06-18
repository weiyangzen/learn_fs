# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtrans2find.c

Implements server-side TRANS2 directory search operations and search handle lifecycle.

Key points:
- `smbsearchnew`, `smbsearchclose`, and related helpers manage `SmbSearch` handles in the session SID map.
- `standardflatten` emits `SMB_INFO_STANDARD` directory entries with DOS date/time fields.
- `findbothflatten` emits `SMB_FIND_FILE_BOTH_DIRECTORY_INFO` records with NT times, allocation size, attributes, name length, short-name fields, and alignment.
- `populate` walks cached directory entries, applies SMB wildcard matching, flattens records, and stops on count or output-buffer exhaustion.
- `smbtrans2findfirst2` parses search parameters, splits path/pattern, builds a directory cache, creates a search handle when needed, and returns SID/count/EOS/name offset.
- `smbtrans2findnext2` resumes a prior search, optionally repositions by filename, and closes the search on requested flags or end-of-search.

Dependencies:
- Uses `SmbDirCache`, `Reprog`, tree/fid/sid maps, SMB transaction buffers, and Plan 9 `Dir`.

Notable behavior:
- Supports only `SMB_INFO_STANDARD` and `SMB_FIND_FILE_BOTH_DIRECTORY_INFO`.
- Has `poolcheck(mainmem)` instrumentation.
