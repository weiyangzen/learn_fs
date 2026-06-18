# File Research: sources/os/plan9/plan9/sys/src/cmd/ratfs/ctlfiles.c

Parses ratfs configuration/control files and populates synthetic address directories.

Main functions:
- `getconf()` reads `conffile`, currently processing `ournets`, and populates permanent trusted CIDR pseudo-files under `trusted`.
- `reload()` reads `ctlfile`, clears prior counts, maps actions (`allow`, `block`, `deny`, `dial`, `delay`, aliases), and inserts IP/account entries under the corresponding action directory.
- `getline()` canonicalizes each line into lowercase NUL-separated tokens, strips comments, commas, and whitespace, and handles backslash escapes.
- `findkey()` maps token strings through a `Keyword` table.
- `cidrparse()` parses IPv4 CIDR strings, accepting `/` or `#`, and derives a minimal mask if omitted.
- `subslash()` converts `/` to `#` for path-safe names.
- `acctinsert()` inserts account pseudo-file entries, rejecting broad dangerous patterns like `*`, `!`, and variants.
- `ipinsert()` inserts IP/CIDR pseudo-file entries and stores parsed address/mask.
- `ipsort()` sorts IP address arrays and assigns base qids.

Risk/notes:
- `reload()` distinguishes account rules by leading `*`; otherwise treats values as IP/CIDR.
- Address directories store dense arrays; qid assignment depends on sorted counts.
- Permanent trusted entries are rebuilt on config reload, while temporary entries are preserved/re-qid’d.
