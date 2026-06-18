# File Research: sources/local-fs/xfsdump/common/content.h

Purpose: defines the content-layer abstraction and shared content media header for dump and restore.

Key contents:
- Defines `content_hdr_t`, which occupies `media_hdr_t.mh_upper`.
- Header fields include mount point, filesystem device, filesystem type, filesystem UUID, content strategy id, and `ch_specific` strategy-private bytes.
- Defines quota output filenames:
  - `xfsdump_quotas`
  - `xfsdump_quotas_proj`
  - `xfsdump_quotas_group`
- Under `DUMP`, defines `quota_info_t` and dump-side entry points:
  - `content_init(argc, argv, gwhdrtemplatep)`
  - `content_stream_dump(strmix)`
  - `is_quota_file(ino)`
- Under `RESTORE`, declares restore-side state and entry points:
  - `perssz`
  - `content_init(argc, argv, vmsz)`
  - `content_stream_restore(thrdix)`
  - `content_overwrite_ok`
  - `content_showinv`
  - `content_showremainingobjects`
- Common declarations include:
  - `content_complete`
  - `content_statline`
  - `content_media_change_needed`
  - `content_mediachange_query`

Important details:
- `CONTENT_STATSZ` must match `DLOG_MULTI_STATSZ` in `dlog.h` according to the comment, making status-line sizing cross-header coupled.
- `ch_specific` is where inode-strategy metadata from `content_inode.h` is embedded.

Risks/notes:
- The struct layout is on-media format. Field size or order changes affect backward compatibility and translation code.
