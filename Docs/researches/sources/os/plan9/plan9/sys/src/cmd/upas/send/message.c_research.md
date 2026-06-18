# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/message.c

## Purpose
Message parsing, storage, header normalization, and output formatting for `upas/send`.

## Main Interfaces
- `m_new`, `m_free`: message lifecycle.
- `default_from`: default sender/date setup.
- `m_read`: reads interactive, local, or rmail input.
- `rfc822cruft`: parses headers, records header flags, removes equivalent systems in addresses, detects bulk.
- `m_get`: chunked access to in-memory/temp-file message body.
- `m_print`, `m_bprint`: output message with remote/local/mbox formatting.

## Behavior
Messages up to about 64 KiB stay in memory; larger bodies spill to a temp file, with a 128 MiB limit. Remote `From` lines are parsed for sender/date. RFC822 parser output is used to detect existing Date/From/MIME/Subject/To fields and rewrite equivalent bang paths. Output adds Unix/remote headers, Date, From, To, and UTF-8 MIME headers when needed, and escapes `From ` lines for mbox delivery.

## Dependencies
SMTP parser (`y.tab.h`), regexps `FROMRE`/`REMFROMRE`, `skipequiv`, temp-file helpers, `String`.

## Risks / Notes
- Oversized messages are represented by `mp->size < 0` and rejected by caller.
- UTF-8 detection is any byte with high bit set, not full UTF-8 validation.
