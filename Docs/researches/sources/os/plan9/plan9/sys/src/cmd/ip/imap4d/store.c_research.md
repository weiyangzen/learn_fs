# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/store.c

Implements IMAP `STORE` flag mutation and flag response emission.

Key behavior:
- `storeMsg` applies replace/add/remove flag operations from a `Store` descriptor to a message.
- `\Recent` is protected from client mutation by preserving the old `MRecent` bit.
- `setFlags` updates a message, marks the `.imp` metadata dirty, and maintains `box->recent`.
- `sendFlags` emits untagged `FETCH FLAGS` updates for messages marked `sendFlags`.
- `writeFlags` serializes system flags in IMAP form.
- `msgSeen` marks a message seen as a fetch side effect and schedules a flag update.
- `mapFlag` maps IMAP flag names to internal bitmasks.

Integration points:
- Mutations rely on caller holding the `.imp` lock when persistence is required.
- Uses `bout`, `Bprint`, and shared flag constants from `imap4d.h`.

Risks and notes:
- Silent store operations still update persistent state but suppress immediate flag response.
- Keyword support is bitmask-based through parser-supplied `Store.flags`; arbitrary custom keyword strings are not visible here.
