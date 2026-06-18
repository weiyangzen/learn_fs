# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/fs/dat.h

- Role: Core data model for `upas/fs`, the mail-as-filesystem service.
- Key types: `Message` tree with raw/header/body/MIME metadata, RFC822 fields, refs, digest, IMAP UID, POP UIDL; `Mailbox` with lock, refs, root message, version, callbacks, and backend aux data; `Hash` directory lookup entries.
- Constants: Message subfile qid types (`Qbody`, `Qheader`, `Qinfo`, etc.), top/mailbox/control qid types, encoding/disposition enums, and `PATH`/`FILE` qid helpers.
- Integration: Shared by `fs.c`, `imap4.c`, and other mailbox backends.
- Risks/notes: Many fields are raw pointers into message buffers, so lifetime and parse ownership are central correctness constraints.
