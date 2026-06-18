# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/fetch.c

This file implements IMAP FETCH response generation.

Key behavior:
- `fetchseen` marks messages seen for fetch operations that read bodies/text.
- `fetchmsg` validates requested fetch items, loads message structure as needed, and emits `FETCH` tuples for flags, UID, envelope, internal date, body/bodystructure, RFC822 variants, size, and body sections.
- `fetchsect` prints section selectors and resolves nested MIME message parts.
- `fetchbody` serves headers, MIME headers, raw body, text, whole body, partial ranges, and selected header fields; it maps LF to CRLF while streaming.
- `fetchbodypart` emits literal size and optional partial offset.
- `fetchenvelope`, `fetchbodystruct`, `Bmime`, `Bimapaddr` serialize IMAP envelope/bodystructure/address data.

Integration and risks:
- Uses parsed `Msg`, `Header`, MIME, and address structures from the IMAP daemon mailbox layer.
- Partial fetch over LF-to-CRLF conversion requires reading through the stop point because output position differs from file offset.
