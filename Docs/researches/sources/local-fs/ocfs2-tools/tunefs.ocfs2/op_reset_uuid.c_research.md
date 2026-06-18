# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_reset_uuid.c

## Role

Implements `-U/--uuid-reset[=new-uuid]`, resetting the OCFS2 volume UUID either to a generated UUID or to a user-supplied UUID.

## Accepted UUID Forms

The parser accepts:

- 32 hex digits without dashes
- 36-character conventional UUID form with dashes

`translate_uuid()` converts the 32-character form to the dashed 36-character form before `uuid_parse()`.

## Run Flow

`reset_uuid_parse_option()` validates any supplied UUID and stores the original argument pointer in `op->to_private`.

`update_volume_uuid()` prompts the user. If a custom UUID was supplied, it adds a critical warning about duplicate UUID danger. It then starts progress, generates or parses the UUID, copies it into `s_uuid`, and writes the superblock under signal blocking.

## Metadata Touched

- `OCFS2_RAW_SB(fs->fs_super)->s_uuid`
- Superblock write via `ocfs2_write_super()`

## Open Flags

Declared as `TUNEFS_FLAG_RW`.

## Notable Risks

- If `uuid_parse()` failed inside `update_volume_uuid()` after progress start, progress cleanup would be skipped. Normal CLI parse validation should prevent this path for supplied UUIDs.
- The operation stores `arg` directly rather than copying it; safe for argv lifetime in this CLI, but not reusable as an independent library API.
