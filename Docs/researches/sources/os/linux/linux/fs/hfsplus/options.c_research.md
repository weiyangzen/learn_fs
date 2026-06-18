# File Research: sources/os/linux/linux/fs/hfsplus/options.c

## Role

Parses, initializes, and displays HFS+ mount options through the Linux `fs_context` parser interface.

## Supported Parameters

The `hfs_param_spec[]` table accepts:

- string options: `creator`, `type`, `nls`;
- numeric options: octal `umask`, `uid`, `gid`, `part`, `session`;
- negatable flags: `decompose` / `nodecompose`, `barrier` / `nobarrier`;
- flag: `force`.

`creator` and `type` must be exactly four bytes and default to `HFSPLUS_DEF_CR_TYPE` (`'????'`).

## Key Functions

- `hfsplus_fill_defaults(struct hfsplus_sb_info *opts)`
  - Sets default creator/type, current umask, current UID/GID, and `part = session = -1`.
  - Returns immediately for a null options pointer.
- `hfsplus_parse_param(struct fs_context *fc, struct fs_parameter *param)`
  - During reconfigure/remount, ignores all options except `force`.
  - Uses `fs_parse()` against `hfs_param_spec`.
  - Validates fixed-length creator/type strings.
  - Stores uid/gid values and sets `HFSPLUS_SB_UID` / `HFSPLUS_SB_GID`.
  - Loads `nls` once and rejects attempts to change an already loaded NLS mapping.
  - Handles `nodecompose` via negated `decompose`; negated `decompose` sets `HFSPLUS_SB_NODECOMPOSE`, while plain `decompose` clears it.
  - Handles `nobarrier` via negated `barrier`; negated `barrier` sets `HFSPLUS_SB_NOBARRIER`, while plain `barrier` clears it.
  - Sets `HFSPLUS_SB_FORCE` for `force`.
- `hfsplus_show_options(struct seq_file *seq, struct dentry *root)`
  - Emits non-default creator/type, umask/uid/gid, partition/session, loaded NLS charset, `nodecompose`, and `nobarrier`.

## Dependencies

Uses Linux `fs_parser`, `fs_context`, NLS loading, seq-file option display, current credentials/umask helpers, and HFS+ superblock flags.

## Research Notes

Option parsing feeds directly into mount-time behavior in `super.c` and Unicode behavior in `unicode.c`. `force` is intentionally the only effective remount option; other parsed mount fields are immutable for an existing mount.
