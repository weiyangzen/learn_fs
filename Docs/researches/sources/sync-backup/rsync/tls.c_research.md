# sources/sync-backup/rsync/tls.c

Purpose: `tls` is a deterministic test-listing utility used by the rsync tests instead of platform `ls`, avoiding OS-specific output and symlink metadata quirks.

Important APIs/types/functions: defines stub globals required by shared syscall code. `stat_xattr()` optionally overlays fake-super stat data from `user.rsync.%stat`/`rsync.%stat`. `storetime()` formats UTC timestamps or fixed-width blanks. `list_file()` performs `do_lstat()`, optional create-time/fake-super handling, symlink target reading, permission formatting, size/device formatting, and output. `tls_usage()` and `main()` use popt for `--atimes`, `--crtimes`, `--link-times`, `--link-owner`, `--fake-super`, `--nsec`, and help.

Control flow and state: process-global flags control displayed metadata. Each command-line file is listed independently; the tool does not recurse or read directories. Symlink mode bits, owner, and mtime are masked unless options request them for reproducibility.

Dependencies and integration: depends on rsync wrappers (`do_lstat`, `do_readlink`, `permstring`, `do_big_num`), popt, xattr helpers, and optional create-time support. Tests use it for stable comparisons and uid/gid parsing in xattr fake-super tests. Risks include fixed 4096 symlink target buffer truncation for extreme links, fake-super parse hard failure on corrupt xattrs, and platform conditional output differences. Test signals come from many tests that compare `tls` output or parse its columns.
