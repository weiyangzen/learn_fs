# File Research: sources/os/plan9/plan9/sys/src/cmd/ratfs/misc.c

ratfs walking, directory serialization, trusted cleanup, address/account matching, and string interning.

Main logic:
- `walk()` dispatches path lookup by current node kind: normal directory, trusted dir, IP address dir, account dir.
- `dirwalk()` finds named child nodes.
- `trwalk()` matches an input IP against trusted CIDR nodes.
- `ipwalk()` parses an IP path component and binary-searches the sorted address table.
- `acctwalk()` parses source-routed account paths into domains plus user and matches against account patterns.
- `ipsearch()` searches CIDR entries sorted by base IP.
- `dread()` serializes real child nodes for directory reads.
- `hread()` serializes address-array pseudo-files using the shared `dummy` Dir.
- `finddir()` finds top-level directories by type.
- `cleantrusted()` removes expired temporary trusted files after `Timeout`.
- `accountmatch()`, `usermatch()`, and `dommatch()` implement account/domain pattern semantics.
- `atom()` interns strings using a small hash table and bump allocators.

Risk/notes:
- Atomized strings allow pointer comparison in permission checks elsewhere.
- `accountmatch()` temporarily edits the stored pattern string at `!` and restores it.
- `dummy` node reuse means callers must not expect persistent per-address node objects.
