# File Research: sources/os/plan9/9front/sys/src/cmd/ratfs/misc.c

This file contains ratfs path walking, directory read helpers, address matching, trusted-entry cleanup, and string interning.

Key responsibilities:
- `walk()` dispatches path traversal based on node type.
- `dirwalk()` finds static child directories.
- `trwalk()` matches trusted CIDR pseudo-files by masking the requested IP.
- `ipwalk()` parses an IP path element, binary-searches sorted address rules, and returns the shared `dummy` node.
- `acctwalk()` parses source-routed account paths and matches them against account patterns.
- `ipsearch()` performs masked binary search over sorted IP/CIDR entries.
- `dread()` serializes real child nodes for directory reads.
- `hread()` serializes generated address/account pseudo-file directory entries.
- `finddir()` locates top-level directories by type.
- `cleantrusted()` removes expired temporary trusted files after a two-hour timeout.
- `accountmatch()`, `usermatch()`, and `dommatch()` implement domain/user wildcard semantics.
- `atom()` interns strings through a custom permanent string table.

Implementation notes:
- Generated address pseudo-files reuse global `dummy`, mutating its name and QID as needed.
- Account patterns support domain, subdomain, user, and trailing-user-prefix matches.
- The string table intentionally never frees interned strings to support pointer identity comparisons.
