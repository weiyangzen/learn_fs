# File Research: sources/local-fs/jfsutils/libfs/fsckcbbl.h

## Purpose
Defines the fixed communication record between the JFS Clear Bad Block List utility and fsck, stored in the first page of fsck’s in-aggregate workspace block map.

## Key Structure
`struct fsckcbbl_record` is documented as 128 bytes and includes:
- Eyecatcher and reserved bytes.
- Clear-bad-block return code and block-size metadata.
- Fixed metadata/workspace boundary fields: `fs_last_metablk`, `fs_first_wspblk`.
- Bad-block counters: total, resolved, relocated extent count, relocated block count, LVM list count.
- Diagnostic buffer pointer eyecatcher and several pointer fields used by the bad-block utility/fsck implementation.

## Dependencies
Relies on fixed-width integer types but does not include a type header directly; consumers must include suitable definitions before or through surrounding headers.

## Notes
This structure is embedded at the start of `struct fsck_blk_map_hdr` in `fsckwsp.h`. It mixes persistent-looking counters with raw process pointers, so portability depends on the specific writer/reader expectations.
