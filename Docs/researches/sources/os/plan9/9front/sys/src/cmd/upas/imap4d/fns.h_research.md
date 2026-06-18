# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/fns.h

This header declares the IMAP daemon’s cross-file function API.

Key contents:
- Prototypes for formatting, authentication, folder/file helpers, locks, mailbox open/close/list/create/remove/rename, `.imp` parsing/writing, message operations, fetch/search/store/copy/append, modified UTF-7, filesystem encoding, and AVL fstree helpers.
- Declares vararg checking for logging, command formatting, and custom format specifiers.
- Defines allocation convenience macros `MK` and `MKZ`, and `STRLEN`.

Integration and risks:
- This is the shared ABI across most `imap4d` C files.
- Prototypes show broader daemon capabilities beyond this group, including search/store/list/quota/parser support.
