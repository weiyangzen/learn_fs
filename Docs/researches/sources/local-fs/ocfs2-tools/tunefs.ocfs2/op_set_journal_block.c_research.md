# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_set_journal_block.c

## Role

Implements journal block mode toggles exposed through `-J block64`, `-J block32`, `-J noblock64`, and `-J noblock32`.

## Operations

`set_journal_block32_run()` clears `JBD2_FEATURE_INCOMPAT_64BIT` from journal feature options by passing a mask with no corresponding option bit. It refuses block32 mode if the filesystem has more than `UINT32_MAX` blocks.

`set_journal_block64_run()` enables `JBD2_FEATURE_INCOMPAT_64BIT` for all journals and also sets `OCFS2_FEATURE_COMPAT_JBD2_SB` in the OCFS2 superblock before resizing/updating journals.

Both paths call `tunefs_set_journal_size(fs, 0, mask, options)`, where size zero means preserve or infer current journal sizing while updating features.

## Metadata Touched

- Journal superblock feature bits through `tunefs_set_journal_size()`
- OCFS2 superblock `s_feature_compat` for block64 enablement
- Superblock write on block64 path

## Open Flags

Both operations require `TUNEFS_FLAG_RW | TUNEFS_FLAG_ALLOCATION`.

## Notable Risks

- The block64 path writes the OCFS2 superblock before updating all journal feature bits. If the journal update then fails, the filesystem may have partially advanced compatibility metadata.
- Error message says “more that” rather than “more than”; cosmetic only.
