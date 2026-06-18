# sources/sync-backup/rsync/testsuite/xattrs_test.py

Purpose: comprehensive xattr transfer test, also serving as the hard-link xattr variant when invoked through a name containing `hlink`.

Important APIs and flow: skips without xattr support, builds source/check/link/destination trees, parses `tls` output to discover uid/gid for fake-super `%stat`, and seeds many file/dir xattrs including short, long, equal, changed, extra, and rsync-prefixed values. It snapshots expected xattrs with `xattr_dump()`. It verifies simple `-avX --super`, then `--copy-dest` or `--link-dest` with optional `-H`, then `--fake-super --link-dest`, then no-user-permission fake-super/chmod handling. The tail tests xattr behavior across local copies, delete/update, alternate destination, and final update rounds. The hlink variant additionally verifies inode link counts using `rsync_ls_lR`.

State and persistence: heavily mutates `FROMDIR`, `CHKDIR`, `TODIR`, and `lnkdir`, repeatedly changing CWD and removing trees. Expected xattr snapshots are stored in `SCRATCHDIR/xattrs.txt`.

Dependencies and integration: exercises almost every major path in `xattrs.c`: collection, filtering, interning, long-value checksums, request/response, setting/removal, fake-super stat xattrs, alt-dest, hard links, and permission workarounds. Risks include platform xattr namespaces, permission model differences, hard-link capability, and exact dump ordering. Test signal is repeated exact dump equality plus hard-link sanity.
