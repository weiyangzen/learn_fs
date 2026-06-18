# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/scanmail/scanmail.c

## Purpose
Mail scanner/filter that canonicalizes incoming mail, applies spam/hold/dump patterns, and then queues or drops/copies mail.

## Main Interfaces
- `main`: parses scanner options, loads patterns, canonicalizes message, evaluates actions, and calls `qmail`.
- `qmail`: streams buffered and remaining message data into `qer` or `/dev/null`.
- `matchaction`, `matcher`: apply action-specific patterns to command, header, and body.
- `saveline`, `opendump`, `opencopy`: logging/copy side effects.
- `optoutofspamfilter`: per-recipient opt-out check.

## Behavior
The scanner builds a lowercased command string from sender and recipients, canonicalizes header/body, skips filtering if all recipients have `nospamfiltering`, runs `Lineoff` first, then applies actions in priority order. `Hold` changes queue directory to hold queue; `Dump` suppresses queueing and optionally saves a dump; `SaveLine` logs matched context.

## Dependencies
`qer`, `UPASLIB/patterns`, `UPASLOG/lines`, spool directories, common scanner engine.

## Risks / Notes
- Opt-out is all-recipient based: if every recipient opts out, patterns are skipped.
- `Dump` mutates the match buffer by writing NUL at match end for logging.
