# File Research: sources/os/linux/linux-stable/fs/isofs/rock.c

Implements Rock Ridge / SUSP parsing for names, inode attributes, relocation, symlinks, and zisofs metadata.

Key infrastructure:
- `struct rock_state` tracks the current System Use area, continuation area, allocated continuation buffer, loop count, and inode.
- `setup_rock_ridge()` positions parsing after the ISO directory record name and optional Rock Ridge skip offset.
- `check_sp()` validates the SP magic and stores the SUSP skip offset.
- `rock_continue()` follows CE continuation records with bounds checks, volume bounds checks, and a `RR_MAX_CE_ENTRIES` loop cap.
- `rock_check_overflow()` validates minimum record sizes before field access.

Key consumers:
- `get_rock_ridge_filename()` extracts NM alternate names, supports continued names, truncates over `NAME_MAX`, ignores `.`/`..`, and returns `-1` for relocated-directory RE entries.
- `parse_rock_ridge_inode()` calls the internal parser, retrying after XA attributes when the SP offset is still unknown.
- `parse_rock_ridge_inode_internal()` handles PX permissions/ownership/links, PN device numbers, TF timestamps, SL symlink size accounting, CL relocated directories, RE relocation placeholders, ER extension recognition, and ZF compressed-file metadata.
- `rock_ridge_symlink_read_folio()` rereads the directory record and assembles symlink content from SL records and continuations into the folio.

Important safeguards:
- Malformed RR lengths often cause Rock Ridge data to be ignored rather than making files invisible, but verified overflows return `-EIO`.
- Recursive/self directory relocation is rejected.
- Symlink assembly checks page bounds and fails if the link would overflow the page.
- ZF compression is ignored when `nocompress` is set or when block shift is unsupported.
