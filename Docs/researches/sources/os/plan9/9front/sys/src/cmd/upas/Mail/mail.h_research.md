# File Research: sources/os/plan9/9front/sys/src/cmd/upas/Mail/mail.h

This header defines the shared data model for the Acme `Mail` program.

It declares `Event`, `Win`, `Comp`, `Mesg`, and `Mbox`. `Win` wraps Acme file descriptors and I/O helpers. `Comp` adds marshal pipe state and reply metadata. `Mesg` stores mailbox identity, open/delete state, threading relationships, multipart parts, and parsed mail headers. `Mbox` stores message arrays, message-id hash table, open windows, plumber channels, view mode, and mailbox path.

It also defines state/flag enums (`Sopen`, `Szap`, `Fseen`, `Ftodel`, etc.), view modes, stack/buffer sizes, globals, and function prototypes for window, message, mailbox, compose, and utility modules.
