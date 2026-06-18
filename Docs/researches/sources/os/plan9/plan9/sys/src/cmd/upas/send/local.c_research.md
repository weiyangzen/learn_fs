# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/local.c

## Purpose
Local-address expansion logic for forwarding files, `pipeto`, and mailbox existence.

## Main Interfaces
- `expand_local`: resolves one local destination after rewrite produced `d_cat`.

## Behavior
Rejects `/../` paths, determines local user, fills default mailbox path if needed, optionally reads a `forward` file and returns expanded destinations, detects `pipeto` and rewrites the destination to execute that script, or marks destination `d_cat` if the mailbox directory exists.

## Dependencies
`mboxpath`, `mboxname`, `sysopen`, `sysexist`, `s_to_dest`.

## Risks / Notes
Comment notes `pipeto` shell construction is unsafe for account names with special characters, though earlier address escaping mitigates some cases.
