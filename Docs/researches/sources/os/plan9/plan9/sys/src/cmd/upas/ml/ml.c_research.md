# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/ml/ml.c

## Purpose
Mailing-list remailer for normal list submissions.

## Behavior
Reads a message from stdin, discards the Unix `From ` line, reads up to 2 MiB, parses headers, determines sender, rejects mail from the list address itself, adds sender to in-memory recipients, starts `upas/send`, writes a modified message, waits for the mailer, and appends to the list mailbox archive if it exists.

## Key Functions
- `printmsg`: suppresses original `Reply-To` and `Precedence`, rewrites subject with `[list]`, adds `Reply-To` and `Precedence: bulk`.
- `appendtoarchive`: appends original first line and message to list mbox if present.
- `printsubject`: prefixes subject with `[list]` unless already present.

## Dependencies
Mailing-list common helpers, RFC822 parser globals, `/bin/upas/send`.

## Risks / Notes
Only the first 2 MiB are read, so larger submissions are truncated.
