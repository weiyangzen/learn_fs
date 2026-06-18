# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/imap4d.h

Shared data model for `imap4d`. It defines mailbox `Box`, message `Msg`, MIME/header/address structures, mailbox lock state, named integer maps, constants for buffer sizes, digest/UID/flag field widths, mailbox/message name limits, modified UTF-7 sizing, message flags, and bogus-message flags.

It also defines parse-tree structures for FETCH, BODY sections, STATUS items, STORE, SEARCH, numeric/string lists, message sets, and byte ranges, then includes `bin.h` and `fns.h` to expose parser allocation state, global I/O buffers, user/mailbox globals, and daemon helper prototypes.
