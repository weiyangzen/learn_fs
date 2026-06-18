# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/list.c

Implements IMAP `LIST`, `LSUB`, and subscription maintenance for Plan 9 `imap4d`, mapping mailbox names onto `/mail/box/$user` entries and emitting IMAP mailbox list responses.

Key behavior:
- `lsubBoxes` reads `imap.subscribed`, creates it with default `INBOX` via `mkSubscribed` if absent, and filters each subscribed mailbox through `checkMatch`.
- `subscribe` updates `imap.subscribed` under the mailbox lock, normalizing `inbox` to `INBOX`.
- `listBoxes` always checks `INBOX`, then delegates wildcard traversal to `listMatch`.
- `listMatch` implements IMAP wildcard traversal for `%` and `*`, avoiding full recursion for `%` and only doing recursive-ish listing for `*`.
- `listAll` is intentionally non-recursive in practice because recursive call is guarded by `if(0 && ...)`; it lists one level and lets `checkMatch` filter.
- `mayMatch` and `matches` implement UTF-aware segment wildcard matching over `/`-separated mailbox names.
- `checkMatch` validates with `okMbox`, computes flags such as `\Noselect`, `\Noinferiors`, and `\Marked`, encodes mailbox names using modified UTF-7, and writes untagged IMAP responses.

Integration points:
- Depends on mailbox locking and path helpers from `imap4d.h`/utils: `mbLock`, `mbUnlock`, `cdOpen`, `cdDirstat`, `cdCreate`, `readFile`, `okMbox`, `impName`, `strmutf7`.
- Uses global `mboxDir` and output `bout`.

Risks and notes:
- `subscribe` opens `tfd` with truncation but writes via `fd`, relying on both descriptors pointing at the same file; this is unusual and worth care if porting.
- Wildcard matching is byte-preserving for multibyte UTF by copying rune byte counts, but pattern semantics are custom.
- Mailbox filtering explicitly hides mail-internal directories such as `mails`, `out`, `obox`, and `.imp`.
