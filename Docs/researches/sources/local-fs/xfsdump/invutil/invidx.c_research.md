# File Research: sources/local-fs/xfsdump/invutil/invidx.c

Implements invutil operations for inventory index entries and import/merge behavior across `.InvIndex` and `.StObj` files.

Key functions:
- `generate_invidx_menu()` opens/maps an index file, creates one node per `invt_entry_t`, and generates child storage-object menus.
- `invidx_commit()` handles deletion of native index entries, importing new entries, copying storage objects, and merging overlapping imported time ranges.
- Merge helpers read sessions from source stobjs and insert them into destination stobjs, splitting full storage objects as needed.
- `read_stobj_info()`, `insert_stobj_into_stobjfile()`, `delete_stobj_entries()`, `find_stobj_insert_point()`, and `update_invidx_entry()` implement raw stobj editing for import/merge.
- `find_overlapping_invidx()` and `find_invidx_insert_pos()` place imported index entries by time range.
- `remmap_invidx()`, `open_invidx()`, `close_invidx()`, and `close_all_invidx()` manage locked, mmap-backed index files.
- Local copies of `stobj_create()` and `stobj_put_streams()` support creating/rewriting storage objects during invutil import.

Important dependencies:
- Uses global `stobj_file` state from invutil’s stobj module.
- Uses raw private inventory structures and offset macros from `inv_priv.h`.
- Uses shell `cp` via `system()` for shortcut storage-object file copies when no merge is needed.

Notable observations:
- The import path has two modes: copy whole stobj files for non-overlap, or merge individual sessions for overlap.
- Some insertion/copy code assumes streams and mediafiles are present; `insert_stobj_into_stobjfile()` returns early if any of `hdr`, `ses`, `strms`, or `mfiles` is null, so zero-stream or zero-media sessions may not import through that path.
- `remmap_invidx()` uses a size expression similar to fstab remap; it grows capacity by `num` but maps `(nEntries + 1) * (num * sizeof(entry)) + counter`, which only behaves as expected for `num == 1`.
- Shell command construction for `cp` is not quoted, so paths with spaces or shell metacharacters would be unsafe.
