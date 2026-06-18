# File Research: sources/os/linux/linux-stable/fs/hfsplus/options.c

## Role

Mount option defaults, parsing, and display for the HFS+ filesystem.

## Supported Options

The parser accepts:

- `creator=<4 chars>`
- `type=<4 chars>`
- `umask=<octal>`
- `uid=<u32>`
- `gid=<u32>`
- `part=<u32>`
- `session=<u32>`
- `nls=<charset>`
- `decompose` / negated form via `fsparam_flag_no`
- `barrier` / negated form via `fsparam_flag_no`
- `force`

## Key Functions

- `hfsplus_fill_defaults(struct hfsplus_sb_info *opts)`
  - Sets creator/type to default `'????'`.
  - Uses current process umask, uid, and gid.
  - Sets partition and session to `-1`.
- `hfsplus_parse_param(struct fs_context *fc, struct fs_parameter *param)`
  - During reconfigure, ignores every option except `force`.
  - Uses `fs_parse()` with `hfs_param_spec`.
  - Validates `creator` and `type` are exactly four characters, then copies raw bytes into 32-bit fields.
  - Sets mount UID/GID and corresponding override flags.
  - Stores partition/session selectors.
  - Loads NLS table once; refuses changing NLS after it is already set.
  - Handles `decompose` negation by setting `HFSPLUS_SB_NODECOMPOSE`; non-negated clears it.
  - Handles `barrier` negation by setting `HFSPLUS_SB_NOBARRIER`; non-negated clears it.
  - Sets `HFSPLUS_SB_FORCE` for `force`.
- `hfsplus_show_options(struct seq_file *seq, struct dentry *root)`
  - Emits non-default creator/type, always emits umask/uid/gid, emits optional part/session/nls, and displays `nodecompose`/`nobarrier` when those flags are set.

## Dependencies

Uses Linux fs-context/fs-parser, NLS loading, seq-file display helpers, mount/user namespace ID display, and HFS+ private superblock state.

## Research Notes

The option model maps positive user-facing `decompose` to clearing the internal `NODECOMPOSE` flag. The internal flag means “do not decompose” in Unicode paths, so code often computes `decompose = !NODECOMPOSE`. `nobarrier` suppresses block-device flushes in fsync/sync paths.
