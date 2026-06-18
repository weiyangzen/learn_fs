# File Research: sources/os/plan9/9front/sys/src/lib9p/parse.c

## Read Status
Complete: 116 lines read.

## Purpose
Implements parsing and dispatch helpers for text control commands written to 9P control files.

## Main Responsibilities
- Count whitespace-separated command fields.
- Allocate a combined command buffer, argv vector, and copied command text.
- Tokenize command text.
- Build detailed command error responses quoting original arguments.
- Match parsed commands against a command table.

## Important Functions
- `parsecmd`: returns a `Cmdbuf` with tokenized fields.
- `respondcmderror`: formats an error message including the reconstructed command.
- `lookupcmd`: finds a matching `Cmdtab`, supports wildcard `*`, and validates argument counts.

## Dependencies and Interactions
- Used by servers implementing ctl-style files.
- Uses `tokenize`, `%q` formatting via `quotefmtinstall`, and lib9p `respond`.
