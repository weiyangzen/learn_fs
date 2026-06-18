# File Research: sources/local-fs/xfsdump/common/arch_xlate.h

Purpose: public declarations for architecture/endian translation functions used on xfsdump media, content, record, inomap, and inventory structures.

Key contents:
- Includes all structure definitions needed by translation callers: `types.h`, `global.h`, `content.h`, `content_inode.h`, `drive.h`, `media.h`, `inomap.h`, `rec_hdr.h`, `inv_priv.h`, and `swap.h`.
- Declares translation functions for global/drive/media/content headers and content-inode strategy headers.
- Declares conversion helpers for start points, inomap hunks, file/stat/extent/dirent/xattr/record headers.
- Declares inventory conversion helpers for session headers, sessions, breakpoints, streams, and media files.

Important details:
- Comments document layering: `global_hdr.gh_upper` contains `drive_hdr`, `drive_hdr.dh_upper` contains `media_hdr`, `media_hdr.mh_upper` contains `content_hdr`, and `content_hdr.ch_specific` contains `content_inode_hdr`.
- The header explicitly warns that `global_hdr.gh_upper` must be handled elsewhere because its contents are unknown at the global layer.

Risks/notes:
- This header exposes many concrete serialized types, so changes ripple across dump/restore media compatibility code.
