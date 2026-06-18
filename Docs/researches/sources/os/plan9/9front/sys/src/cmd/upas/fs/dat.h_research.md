# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/dat.h

This header defines the central `upas/fs` mailbox/message data model, constants, backend vtable, qid layout, and shared prototypes.

Key contents:
- Defines cache state flags, content-transfer encodings, content dispositions, deletion states, limits, and mailbox remove flags.
- `Idx` stores indexed top-level message metadata such as digest, flags, fileid, headers, MIME info, size, raw body size, bad char count, and backend aux data.
- `Message` embeds `Idx` and adds cache pointers, MIME tree linkage, reference counts, deletion/in-mailbox state, Unix header fields, charset/boundary, and backend-specific union.
- `Mailbox` stores global mailbox state, root message, digest AVL tree, qids, backend callbacks, LRU cache data, and sync state.
- Declares backend initializers for plan9 mbox, POP3, IMAP4, and mdir.
- Defines qid file IDs for message pseudo-files and `PATH/FILE` macros.
- Declares hash-table lookup helpers and many cross-file functions.

Integration and risks:
- This is the ABI between `fs.c`, `mbox.c`, backends, index code, remove/rename, and MIME parsing.
- `PATH(id, f)` packs file type in low 10 bits; adding more `Q*` values must respect that.
