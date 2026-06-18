# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/metadata_object.c

## Role

`metadata_object.c` implements libFLAC's in-memory metadata object API. It creates, clones, deletes, compares, validates, and mutates `FLAC__StreamMetadata` blocks for STREAMINFO, APPLICATION, SEEKTABLE, VORBIS_COMMENT, CUESHEET, PICTURE, and unknown metadata.

## Major Functions

- `FLAC__metadata_object_new()` allocates and initializes metadata blocks, including default vendor strings and empty picture strings.
- `FLAC__metadata_object_clone()` performs deep copies of variable-sized fields.
- `FLAC__metadata_object_delete_data()` and `FLAC__metadata_object_delete()` release block-owned allocations.
- `FLAC__metadata_object_is_equal()` dispatches to block-type-specific comparators.
- APPLICATION, SEEKTABLE, VORBIS_COMMENT, CUESHEET, and PICTURE setter APIs resize arrays, insert/delete elements, copy or take ownership, and recalculate metadata block lengths.
- Cuesheet helpers calculate CDDB IDs and delegate legality checks to `FLAC__format_cuesheet_is_legal()`.
- Picture legality is delegated to `FLAC__format_picture_is_legal()`.

## Important Implementation Details

The file has a strong copy-first pattern: setters usually allocate or copy new data before freeing old storage so allocation failure leaves objects unchanged. APIs support both `copy=true` and ownership-transfer mode, with Vorbis comments using a const-stripping workaround when taking ownership because the public API source pointer is const.

Length fields are maintained manually after every structural mutation. Seektable length is `num_points * FLAC__STREAM_METADATA_SEEKPOINT_LENGTH`; Vorbis comments include vendor length, comment count, per-comment lengths, and payloads; cuesheets sum fixed track/index fields; picture setters adjust length by old/new string or data lengths.

The resize helpers use `realloc()` and explicit overflow checks against `UINT32_MAX / sizeof(type)`. Growing seektables initializes new seek points as placeholders; growing Vorbis comments creates empty NUL-terminated entries; growing cuesheet arrays zeroes new tracks/indices.

## Risks / Edge Cases

- Many public APIs rely on `FLAC__ASSERT()` for correct object type, bounds, non-null inputs, and pointer/length consistency.
- Ownership-transfer mode mutates source Vorbis comment entries to ensure NUL termination, which is subtle because the formal source pointer is const.
- `FLAC__metadata_object_vorbiscomment_resize_comments()` can leave a partially grown comments array if allocating one of the new empty entries fails; it adjusts `num_comments` to cover allocated entries for later cleanup.
- Some checks compare against `UINT32_MAX` while allocation sizes are `size_t`; this follows FLAC metadata length limits but should be reviewed on unusual platforms.
- `FLAC__metadata_object_picture_set_mime_type()` and description setters use `strlen()`, so caller-provided strings must be valid C strings.

## Dependencies

Uses `private/metadata.h`, `private/memory.h`, `FLAC/assert.h`, `share/alloc.h`, and `share/compat.h`. It depends heavily on public format validators and constants from `FLAC/format.h` via `FLAC/metadata.h`.
