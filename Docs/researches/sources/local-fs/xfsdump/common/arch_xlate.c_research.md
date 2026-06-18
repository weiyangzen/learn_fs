# File Research: sources/local-fs/xfsdump/common/arch_xlate.c

Purpose: implements endian/architecture translation for serialized xfsdump media and inventory structures.

Key behavior:
- Uses `IXLATE`/`INT_XLATE` for numeric fields and `BXLATE`/`bcopy` for byte arrays, UUIDs, padding, labels, and opaque upper-layer regions.
- Converts nested media-file header layers:
  - `global_hdr_t`
  - `drive_hdr_t`
  - `media_hdr_t`
  - `content_hdr_t`
  - `content_inode_hdr_t`
- Converts inode-content structures:
  - `startpt_t`
  - inomap `hnk_t`
  - `filehdr_t`
  - `bstat_t`
  - `extenthdr_t`
  - `direnthdr_t`
  - `direnthdr_v1_t`
  - `extattrhdr_t`
  - `rec_hdr_t`
- Converts inventory structures:
  - `invt_seshdr_t`
  - `invt_session_t`
  - `invt_breakpt_t`
  - `invt_stream_t`
  - `invt_mediafile_t`

Important details:
- `dir` controls conversion direction. Several functions swap `ptr1`/`ptr2` for debug logging when `dir < 0`, while byte-array copies still copy the unconverted representation to the destination.
- `xlate_global_hdr` deliberately does not interpret `gh_upper`; it only byte-copies it because upper-layer contents depend on the caller.
- `xlate_content_inode_hdr` recursively converts `cih_startpt` and `cih_endpt`.
- `xlate_filehdr` recursively converts embedded `bstat_t`.
- `xlate_hnk` converts all `SEGPERHNK` segment bitmaps and clears `h2->nextp`, avoiding serialized pointer reuse.
- `xlate_invt_stream` and `xlate_invt_mediafile` recursively convert inventory breakpoints.

Interactions:
- Used by `drive_minrmt.c` when writing tape headers and validating/reading media-file and record headers.
- Declared by `arch_xlate.h`; depends on serialized type definitions from `global.h`, `content.h`, `content_inode.h`, `drive.h`, `media.h`, `inomap.h`, `rec_hdr.h`, and inventory private headers.

Risks/notes:
- The translation layer is tightly coupled to exact on-media struct layouts. Adding fields requires updating this file and the corresponding header sizes.
- Opaque byte copies preserve padding and strings, but any newly numeric field placed in an opaque area must be translated at the proper layer.
