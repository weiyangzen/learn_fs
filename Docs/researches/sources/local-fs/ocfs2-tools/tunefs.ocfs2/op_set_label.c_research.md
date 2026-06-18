# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_set_label.c

## Role

Implements `-L/--label <label>`, changing the OCFS2 volume label in the superblock.

## Parse Flow

`set_label_parse_option()` requires an argument and stores the argv pointer in `op->to_private`.

## Run Flow

`update_volume_label()` compares the requested label against the current superblock label, including NUL when possible, and skips work if already matching. Otherwise it prompts, starts progress, zeroes `s_label`, copies the requested label truncated to `OCFS2_MAX_VOL_LABEL_LEN`, and writes the superblock under signal blocking.

## Metadata Touched

- `OCFS2_RAW_SB(fs->fs_super)->s_label`
- Superblock write via `ocfs2_write_super()`

## Open Flags

Declared as `TUNEFS_FLAG_RW`.

## Notable Risks

- The label argument is not rejected when longer than the max; it is silently truncated.
- The operation stores an argv pointer rather than duplicating the label. This is acceptable for the CLI lifecycle.
