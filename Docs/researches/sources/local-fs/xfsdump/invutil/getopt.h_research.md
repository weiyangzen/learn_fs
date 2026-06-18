# File Research: sources/local-fs/xfsdump/invutil/getopt.h

Defines command-line option constants for `xfsinvutil`.

Key contents:
- `GETOPT_CMDSTRING` is `dilnu:wCFM:m:s:`.
- Defines option characters for debug, interactive, noninteractive, UUID prune, wait for locks, check/prune fstab, force, prune mount point, prune media label, and prune session id.

Notable observations:
- `-n` is marked obsolete in favor of `-F`.
- This header is distinct from `inventory/getopt.h`; option meanings are invutil-specific.
