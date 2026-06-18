# File Research: sources/os/plan9/9front/sys/src/cmd/upas/ned/nedmail.c

Large interactive mail reader/client for upas mailboxes. It opens mailboxes through `/mail/fs`, builds a local message tree, supports command-address ranges/searches, displays MIME parts, mutates flags, deletes/saves/forwards/replies, and can invoke external commands.

Key responsibilities:
- Starts `/bin/upas/fs` if needed and opens a mailbox or singleton message.
- Builds `Message` trees from `/mail/fs/<mbox>` directories and nested MIME part directories.
- Maintains headers, info fields, flags, missing/deleted state, and display metadata.
- Parses interactive commands with message ranges, searches, and command arguments.
- Displays headers, raw messages, processed bodies, MIME trees, HTML via `htmlfmt`, and attachments through plumber.
- Marks messages seen, deleted, answered, stored, and flagged.
- Flushes deletions through `/mail/fs/ctl`.
- Saves messages/parts to folders or files.
- Replies/forwards by constructing `upas/marshal` invocations.
- Supports piping message parts to shell commands and running shell commands with `%` set to message path.

Important components:
- `Message` models top-level messages and MIME children.
- `Ctype` table maps MIME types to display/plumb behavior and file extensions.
- `cmdtab` defines commands such as `p`, `P`, `h`, `H`, `d`, `u`, `q`, `x`, `i`, `y`, `r`, `R`, `a`, `m`, `s`, `w`, `|`, `||`, `!`, `mb`, `k`, `K`, `F`.
- `switchmb()` opens or maps mailboxes and sets `root`, `mbname`, and working directory behavior.
- `dir2message()` synchronizes top-level message lists and detects new/deleted messages.
- `mdir2message()` loads MIME children.
- `parsecmd()` handles address/range/search parsing and command dispatch.
- `pcmd0()` chooses how to render MIME content.
- `flushdeleted()` batches delete commands to `/mail/fs/ctl`.
- `tomailer()`, `rcmd()`, `acmd()`, and `mcmd()` integrate with `upas/marshal`.

Filesystem relevance:
- Deeply tied to `/mail/fs`: message directories expose `info`, `raw`, `rawbody`, `body`, `header`, `flags`, `unixheader`, and other part files.
- Uses qid/path/version checks in `skipscan()` to avoid unnecessary rescans.
- Opens arbitrary mailbox paths by instructing `/mail/fs/ctl`.
- Saves using upas folder/file append helpers.
- Uses plumber paths rooted back to `/mail/fs/<mbox>`.

Notable risks and quirks:
- Many comments document legacy behavior and known botches around ordering, sorting, and mailbox opens.
- `itsallsapesfault()` contains suspicious digit comparison `c <= 9` rather than `c <= '9'`.
- Command parser is powerful but custom; address/search parsing mutates strings and uses global `sstring`.
- Running shell commands and plumb operations are intentional user-facing behaviors.
