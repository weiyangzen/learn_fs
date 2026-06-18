# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/mntent.c

Private replacement for libc mount-entry parsing and writing, derived from util-linux behavior.

It escapes spaces, tabs, newlines, and backslashes as octal sequences for mtab/fstab-style fields, and reverses those escapes when reading. `my_setmntent()` opens a mount table with restrictive umask, `my_addmntent()` appends escaped records, and `my_getmntent()` skips blank/comment lines, parses six mount fields, warns on malformed lines, and stops after `ERR_MAX` soft parse errors.

Notable constraints: `my_getmntent()` uses static storage for both the line buffer and returned `struct my_mntent`, while individual string fields are newly allocated and expected to be freed by callers in surrounding code.
