# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_cloned_volume.c

## Role

Implements `--cloned-volume[=new-label]`, a dangerous recovery/administration operation that changes a cloned OCFS2 volume's UUID and optionally its label without normal cluster coordination.

## Behavior

`cloned_volume()` prompts with `tools_interact_critical()`, generates a new UUID, updates the label, writes the superblock, and reports progress across three steps.

If `new_label` is provided, `update_volume_label()` truncates it to `OCFS2_MAX_VOL_LABEL_LEN` and skips writing when it already matches. If no label is provided, it appends `-cloned` to the current label, truncating the original label if necessary.

`update_volume_uuid()` uses `uuid_generate()` and copies the raw UUID bytes into `s_uuid`.

The operation is defined with `TUNEFS_FLAG_RW | TUNEFS_FLAG_SKIPCLUSTER`, so the main driver can run it when cluster access is intentionally skipped for a cloned volume.

## Metadata Touched

- `OCFS2_RAW_SB(fs->fs_super)->s_uuid`
- `OCFS2_RAW_SB(fs->fs_super)->s_label`
- Superblock write via `ocfs2_write_super()`

## Safety Model

The file explicitly warns that it bypasses cluster software and requires the operator to guarantee no other node is using the filesystem. Writes are wrapped in `tunefs_block_signals()` / `tunefs_unblock_signals()` around the superblock write.

## Notable Risks

- In the no-label path, the suffix check uses `label_buf + len - CLONED_LABEL_LEN`. If the existing label length is shorter than `CLONED_LABEL_LEN`, this forms a pointer before the buffer. That is a real bounds risk.
- Label comparison for provided labels uses the truncated length and may treat a long supplied label as already matching if the stored prefix matches.
