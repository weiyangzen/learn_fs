# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_rrip.c

## Role

Implements Rock Ridge Interchange Protocol handlers used by HSFS SUSP parsing.

## Main Behavior

- Defines `rrip_signature_table` mapping RRIP signatures to handlers: `CL`, `NM`, `PL`, `PN`, `PX`, `RE`, `RR`, `SL`, and `TF`.
- `rrip_dev_nodes()` parses device major/minor numbers from `PN`.
- `rrip_file_attr()` parses mode, nlink, uid, gid, optional inode, and vnode type from `PX`.
- `rrip_file_time()` parses access, modify, and change/attribute times from `TF`, using long or short ISO date forms.
- `rrip_name()` parses alternate names from `NM`, including special `.` and `..` handling.
- `rrip_sym_link()` builds synthetic symlink targets from `SL` components, handling continued components and final slash removal.
- `rrip_namecopy()` asks `parse_sua()` for an RRIP name and falls back to uppercase ISO comparison setup when no alternate name exists.
- `rrip_reloc_dir()` marks relocated directories so the ISO-visible relocated entry is hidden.
- `rrip_child_link()` and `rrip_parent_link()` follow relocated directory links by updating extent LBN and refilling directory metadata.
- `rrip_rock_ridge()` is a placeholder handler for `RR`.

## Important Details

- `name_parse()` is shared by filename and symlink parsing. It handles root/current/parent flags, unsupported volume-root/host flags, continuation/change flags, and binary-safe bounded copying because SUSP fields are not necessarily NUL-terminated.
- Symlink buffers are dynamically allocated according to computed target length and stored in `hs_direntry.sym_link`; `ext_size` becomes symlink length.

## Dependencies And Interactions

- Called from `parse_sua()` in `hsfs_susp_subr.c`.
- Overrides fields initialized by `hs_parsedir()` in `hsfs_node.c`.
- Uses HSFS date parsing helpers from `hsfs_subr.c`.
