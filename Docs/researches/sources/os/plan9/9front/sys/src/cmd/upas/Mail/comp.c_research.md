# File Research: sources/os/plan9/9front/sys/src/cmd/upas/Mail/comp.c

This file manages Acme compose windows for the `Mail` client. `compose()` creates a new window, writes tags, fills headers, optionally quotes a replied-to message body, records reply metadata, and starts `compmain()`.

`compmain()` handles Acme events for compose windows. `Post` reads the body, pipes it to `/bin/upas/marshal -8`, optionally with savebox and reply path options, marks replied-to messages with the answered flag, renames the compose window to `:Sent`, and marks it clean. `Del` checks the Acme dirty flag and requires a second deletion if composing content is still dirty.

Reply generation uses `respondto()` and `show()` to construct `To`/`CC` fields, deduplicating reply-all addresses.
