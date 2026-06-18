# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/imp.c

Implements `.imp` file parsing and writing. `.imp` is the IMAP-specific sidecar format that maps upas/fs message digests to IMAP UIDs and flags.

Key responsibilities:
- Defines `.imp` magic string: `imap internal mailbox description\n`.
- Maps compact on-disk flag characters to IMAP flag bits.
- Parses existing `.imp` files, validates magic/version headers, and applies UID/flag state to currently visible messages by digest.
- Writes current non-expunged messages back to `.imp`.
- Appends or updates a `.imp` entry for copied/appended messages while returning UIDPLUS metadata.

Important functions:
- `parseflags()` converts fixed-width flag strings to bitmasks.
- `impflags()` applies flags, handles `\Recent` cleanup for IMAP-opened boxes, and marks changed flags for unsolicited updates.
- `verscmp()` validates the `.imp` header and advances `uidvalidity`/`uidnext`.
- `parseimp()` builds an AVL digest lookup over current messages, then applies `.imp` entries.
- `wrimp()` writes the complete `.imp` file.
- `appendimp()` opens or creates a mailbox `.imp`, detects duplicates by digest, appends or overwrites the matching entry, and fills `Uidplus`.

Filesystem relevance:
- `.imp` files live under `mboxdir` and are opened via `cdopen()`/`cdcreate()`.
- `.imp` state is keyed by message digest from upas/fs `info`.
- Uses qid/version checks in callers to decide whether `.imp` must be reparsed.

Notable risks and quirks:
- `sreason()` has an off-by-one style condition `r <= nelem(rtab)`.
- Duplicate digest handling logs anomalies and may skip conflicting UIDs.
- `appendimp()` sets `u->uid = box.uidnext` even for duplicate entries, while writing duplicate UID to disk; callers should interpret carefully.
