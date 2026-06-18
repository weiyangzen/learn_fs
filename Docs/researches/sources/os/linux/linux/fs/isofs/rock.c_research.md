# File Research: sources/os/linux/linux/fs/isofs/rock.c

Parses Rock Ridge / SUSP extensions for ISOFS names, POSIX inode metadata, symlinks, relocated directories, timestamps, device numbers, and zisofs compression metadata.

Core scanning support:
- `struct rock_state` tracks current SUSP buffer, continuation area, loop count, and inode.
- `setup_rock_ridge()` positions the scanner at the system-use area, applying discovered `s_rock_offset`.
- `check_sp()` validates the SUSP SP magic and records the skip offset.
- `rock_continue()` validates and reads CE continuation records, limiting to `RR_MAX_CE_ENTRIES` and checking volume/block bounds.
- `rock_check_overflow()` validates minimum record sizes before parsing a signature.

Filename extraction:
- `get_rock_ridge_filename()` scans for NM records, handles continuation, ignores `.`/`..` special NM flags, truncates overlong names, returns `-1` for relocated-directory RE entries, and returns zero if no NM field is found.

Inode parsing:
- `parse_rock_ridge_inode_internal()` handles:
  - ER: marks Rock Ridge as active and logs extension id.
  - PX: POSIX mode, links, uid, gid.
  - PN: special device numbers.
  - TF: create/modify/access/attribute timestamps.
  - SL: computes symlink size.
  - CL: relocated directory target, rejecting recursion/self-reference.
  - RE: rejects direct read of relocated directory placeholders.
  - ZF: marks zisofs-compressed files and records header/block parameters and real size.
- `parse_rock_ridge_inode()` retries with XA offset handling if the initial SP offset was not found and Rock Ridge probing is still tentative.

Symlinks:
- `get_symlink_chunk()` translates SL components into path text, handling normal, `.`, `..`, and root components plus continuation slashes.
- `rock_ridge_symlink_read_folio()` rereads the inode directory record, scans SL records and continuations, writes the target into the folio, and completes the folio read.

Exports `isofs_symlink_aops` with `.read_folio`.
