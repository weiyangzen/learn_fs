# File Research: sources/os/plan9/9front/sys/src/cmd/ratfs/ctlfiles.c

This file parses ratfs configuration and control files into the in-memory policy tree.

Key responsibilities:
- `getconf()` reads the smtpd config file and processes `ournets` entries into permanent trusted-network pseudo-files.
- `reload()` reads the blocked/control file and populates allow, delay, block, dial, and deny address/account directories.
- `getline()` canonicalizes input lines into lower-case, NUL-separated tokens, removing comments, commas, whitespace runs, and simple escapes.
- `findkey()` maps text keywords to action codes.
- `cidrparse()` parses IP/mask or IP#mask names into canonical network and mask values.
- `subslash()` converts `/` to `#` for file-name-safe CIDR strings.
- `acctinsert()` inserts account rules under `account`, rejecting broad dangerous patterns like `*` and `*!*`.
- `ipinsert()` inserts IP/CIDR rules under `ip`.
- `ipsort()` sorts IP entries and assigns base QID ranges for generated pseudo-files.

Implementation notes:
- Permanent trusted entries are purged/reloaded while temporary trusted entries are retained and renumbered.
- Address entries are stored as `Address` arrays on `IPaddr`/`Acctaddr` nodes.
- IP matching depends on sorted arrays and binary search in `misc.c`.
