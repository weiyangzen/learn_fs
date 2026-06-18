# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/metadata.h

Public libFLAC metadata API header, covering metadata reading, editing, chain iteration, callback I/O, and metadata object memory management.

Important contents:
- Includes `sys/types.h` for `off_t`, plus `export.h`, `callback.h`, and `format.h`.
- Documents three metadata access levels:
  - Level 0: filename-based read-only helpers for STREAMINFO, VORBIS_COMMENT, CUESHEET, and constrained PICTURE lookup.
  - Level 1: `FLAC__Metadata_SimpleIterator`, a direct file iterator for reading and editing metadata blocks in place where possible.
  - Level 2: `FLAC__Metadata_Chain` and `FLAC__Metadata_Iterator`, an in-memory full metadata chain interface for editing multiple blocks efficiently before writing.
- Defines status enums and status-string arrays for simple iterator and chain operations.
- Declares Level 1 operations for init, status, writability, traversal, block offset/type/length queries, APPLICATION ID retrieval, block replacement, insertion, and deletion.
- Declares Level 2 operations for reading native FLAC and Ogg FLAC metadata, reading via callbacks, checking whether a tempfile is required, writing via filename/callbacks/tempfile callbacks, and padding merge/sort operations.
- Declares metadata object helpers for allocation, clone, delete, equality, APPLICATION data, SEEKTABLE mutation/template generation/sort/legal checks, VORBIS_COMMENT field construction/search/replacement/removal, CUESHEET track/index mutation/legal checks/CDDB ID, and PICTURE MIME/description/data/legal checks.

Implementation notes:
- This is a declaration and API contract header; actual file rewriting, parsing, allocation, and callback dispatch live elsewhere.
- Metadata object setters use explicit `copy` semantics. If `copy` is false, ownership transfers to the object and the pointer must be compatible with `free()`.
- Returned Level 0 objects and simple-iterator `get_block()` results are caller-owned and must be deleted with `FLAC__metadata_object_delete()`.
- Level 2 iterator `get_block()` returns chain-owned objects; callers must not delete them directly.
- The API warns not to mutate `is_last`, `length`, or `type` on metadata blocks returned from iterator/chain interfaces because those fields are managed internally.
- Callback-based Level 2 reads must be paired with callback-based writes; filename reads must be paired with filename writes. The chain status enum explicitly reports read/write mismatch and wrong write-call cases.
- Ogg FLAC metadata is supported as read-only in this interface.

Filesystem relevance:
- This is not filesystem implementation code, but it has file-update semantics worth noting: metadata edits may rewrite an entire FLAC file, use padding to avoid rewriting, preserve file stats, rename/unlink temp files, or require caller-managed temp handles via callbacks.
- In the 9front tree, this supports bundled FLAC audio metadata tooling rather than kernel or filesystem behavior.
