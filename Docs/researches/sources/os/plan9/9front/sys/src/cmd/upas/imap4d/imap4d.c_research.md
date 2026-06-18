# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/imap4d.c

Implements the top-level IMAP4rev1 daemon command loop, parser, and command handlers for 9front `upas/imap4d`. It is a protocol facade over `/mail/fs`, with mailbox state delegated to `mbox.c`, message rendering to fetch/search/store helpers, authentication to companion auth code, and mailbox naming/listing helpers.

Key responsibilities:
- Initializes `Biobuf` input/output, formatters, authentication flags, server/site identity, and optional preauthentication.
- Maintains IMAP session state tables for non-authenticated, authenticated, and selected mailbox states.
- Dispatches IMAP commands including `CAPABILITY`, `AUTHENTICATE`, `LOGIN`, `APPEND`, `SELECT`/`EXAMINE`, `LIST`/`LSUB`, `FETCH`, `STORE`, `SEARCH`, `COPY`, `EXPUNGE`, `UID`, `IDLE`, `NAMESPACE`, and quota commands.
- Parses IMAP atoms, quoted strings, literals, flags, fetch attributes, store attributes, search keys, sequence sets, dates, and UID sets using a `Bin` allocation arena so parse failures can discard per-command allocations.
- Tracks selected mailbox status, unsolicited `EXISTS`/`RECENT`/`FETCH FLAGS`/`EXPUNGE` updates, and an `IDLE` polling child process.
- Handles UIDPLUS responses for `APPENDUID` and `COPYUID`.

Important implementation details:
- `imap4()` uses `setjmp(parsejmp)` and `parseerr()` for parser recovery.
- `status(expungeable, uids)` carefully avoids sending illegal `EXPUNGE` responses during non-UID `FETCH`/`STORE`/`SEARCH`.
- `idlecmd()` forks an `RFMEM` child that periodically calls `check()` and flushes untagged updates while coordinated by `imaplock`.
- `appendcmd()` accepts optional flags and date, validates mailbox existence, synthesizes a Unix `From ` line, and calls `appendsave()`.
- `searchucmd()` handles `CHARSET`, emits `BADCHARSET` for unsupported charsets, and includes an Apple Mail optimization for immediately searching the last message by `Message-ID`.
- `uidcmd()` supports `UID COPY/FETCH/SEARCH/STORE/EXPUNGE`.
- Literal parsing sends `+ Ready for literal data` and reads exact byte counts from `bin`.

Filesystem relevance:
- Uses mailbox names resolved by `mboxname()` and upas mailbox directories rooted in global `mboxdir`.
- Relies on `checkbox()`, `openbox()`, `closebox()`, `deletemsg()`, `expungemsgs()`, `creatembox()`, `renamebox()`, and `removembox()` to mutate `/mail/fs` state.
- IMAP-visible UID/flag state is not native to `/mail/fs`; it is maintained through `.imp` files elsewhere.

Notable risks and quirks:
- Several comments mark partial or workaround behavior, especially `RENAME`, Apple Mail `Message-ID` search, and mailbox deletion of selected boxes.
- `deletecmd()` contains a suspicious expression `!removembox(mbox) == -1`, likely relying on unintended precedence/boolean behavior.
- Parser is strict ASCII for atoms/quoted strings and has custom handling for line-buffered input.
- `cleaner()` manipulates fds and process notes to stop the idle child and must be called under `imaplock`.
