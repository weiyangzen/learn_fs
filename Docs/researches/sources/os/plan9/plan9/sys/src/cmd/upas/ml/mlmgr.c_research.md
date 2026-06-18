# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/ml/mlmgr.c

## Purpose
Command-line manager for creating mailing lists and adding/removing members.

## Behavior
Supports mutually exclusive `-c listname`, `-a listname addr`, and `-r listname addr`. Creation makes mailboxes for the list and owner, creates `pipeto` scripts pointing to `ml` and `mlowner`, and seeds the address-list file with a comment. Add/remove append entries to the address-list file.

## Key Function
- `createpipeto`: creates executable rc scripts in mailbox `pipeto` files.

## Dependencies
`creatembox`, `mboxpath`, `writeaddr`, Plan 9 `Dir`/`dirfwstat`.

## Risks / Notes
Creation uses simple file writes for executable scripts and reports some stat/wstat failures into the script file itself.
