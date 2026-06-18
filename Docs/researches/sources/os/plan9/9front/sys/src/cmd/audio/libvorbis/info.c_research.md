# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/info.c

Vorbis info/comment/header management implementation. It owns public `vorbis_info` lifecycle, Vorbis comment helpers, header packet parsing, and header packet generation.

Important routines:
- Comment API: `vorbis_comment_init()`, `vorbis_comment_add()`, `vorbis_comment_add_tag()`, `vorbis_comment_query()`, `vorbis_comment_query_count()`, and `vorbis_comment_clear()`.
- Info lifecycle: `vorbis_info_init()`, `vorbis_info_clear()`, and `vorbis_info_blocksize()`.
- Header unpacking: `_vorbis_unpack_info()`, `_vorbis_unpack_comment()`, and `_vorbis_unpack_books()` read the three Vorbis header packet types and validate stream structure.
- Header detection: `vorbis_synthesis_idheader()` checks for an initial Vorbis identification header.
- Main header input: `vorbis_synthesis_headerin()` dispatches identification, comment, and setup headers in correct order.
- Header packing: `_vorbis_pack_info()`, `_vorbis_pack_comment()`, `_vorbis_pack_books()`, `vorbis_commentheader_out()`, and `vorbis_analysis_headerout()`.
- Utility: `vorbis_granule_time()` converts granule positions to seconds; `vorbis_version_string()` returns the general vendor string.

Validation behavior:
- Identification header enforces version 0, positive channels/rate, short block size at least 64, long block size not smaller than short, and maximum long block size 8192.
- Comment unpack checks vendor/comment lengths against packet storage before allocating strings.
- Setup unpack validates codebooks, time backend IDs, floor/residue/mapping backend IDs, mode window/transform types, and mapping indexes.
- On malformed setup, `vorbis_info_clear()` is called to release partial allocations.

Integration points:
- Uses `codec_internal.h`, `codebook.h`, `registry.h`, `window.h`, `psy.h`, `misc.h`, and Ogg bitpacking.
- Backend registries `_floor_P`, `_residue_P`, and `_mapping_P` supply pack/unpack/free hooks.
- Encoding header packets are stored in `private_state` fields `header`, `header1`, and `header2`.

Risk and review signals:
- Some allocation paths do not explicitly handle `_ogg_malloc()`/`_ogg_calloc()` failure.
- `vorbis_comment_query()` returns an interior pointer into owned comment storage, not a copy.
- Cleanup depends on backend type arrays being trustworthy after successful range checking; comments note aborted unpack cases.
- Fuzzing should target truncated headers, large comment counts/lengths, invalid backend indexes, repeated setup headers, and invalid packet ordering.

Filesystem relevance:
- No filesystem implementation. This is stream metadata/header parsing for audio packets.
