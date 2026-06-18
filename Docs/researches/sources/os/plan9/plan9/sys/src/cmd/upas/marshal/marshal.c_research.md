# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/marshal/marshal.c

## Purpose
User-facing message composer/generator. It reads headers/body/attachments, expands aliases, emits MIME/RFC822 output, optionally runs PGP, and streams the result into `upas/send`.

## Main Interfaces
- `main`: option parsing and full compose/send pipeline.
- `readheaders`: preserves and classifies user-supplied headers, strips `Bcc`, optionally extracts recipients from headers.
- `body`, `body64`, `attachment`: body and attachment MIME generation.
- `sendmail`: forks `upas/send` or user `pipefrom`, optionally files a copy.
- `pgpfilter`: inserts `/bin/pgp` between marshal and send.
- `readaliases`, `expand`, `expandline`: personal alias and RFC822 address expansion.
- `rfc2047fmt`, `mksubject`: UTF-8 subject header encoding.

## Behavior
`marshal` can send with command-line recipients or `-8` recipient headers, add default Date/From/To/Cc/Subject/MIME headers, infer attachment content types from builtins, `/sys/lib/mimetype`, or `/bin/file`, construct multipart/mixed messages, and append in-reply-to from a mailfs message directory. It protects typed messages with `holdon/holdoff` and cleans up child processes on fatal errors.

## Dependencies
Plan 9 `Biobuf`, `String`, `Fmt`, mailbox path helpers, `/bin/upas/send`, optional `/bin/pgp`, optional `/bin/file`, and `/sys/lib/mimetype`.

## Risks / Notes
- RFC822 parsing is intentionally partial; malformed address headers set `rfc822syntaxerror`.
- Attachment type inference depends on extension and external `file`.
- The compose path can fork several processes; failures are propagated through wait messages.
