# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/imap4d.c

Main IMAP4rev1 daemon. It initializes buffered stdin/stdout, parses options for preauth, plaintext/password challenge modes, site/remote/server names, and debugging, resolves server/site names, sets notification handling, and enters an IMAP command loop with non-authenticated, authenticated, and selected-state command tables.

Command handlers implement CAPABILITY, LOGIN, AUTHENTICATE CRAM-MD5, APPEND, CREATE, DELETE, RENAME, LIST, LSUB, NAMESPACE, SELECT/EXAMINE, STATUS, CLOSE, EXPUNGE, FETCH, STORE, COPY, SEARCH, UID subcommands, IDLE, NOOP, SUBSCRIBE/UNSUBSCRIBE, and LOGOUT. Selected mailbox state is checked before commands, with EXISTS/RECENT/FLAGS/EXPUNGE updates controlled to respect IMAP restrictions.

The file also owns the hand-written IMAP parser for tags, atoms, quoted strings, literals, message sets, flags, store specs, fetch specs, body sections, partial ranges, and search expressions. It uses parse-bin allocation so failed commands can discard all parse structures at once.
