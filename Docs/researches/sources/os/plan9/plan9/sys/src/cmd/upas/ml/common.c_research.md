# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/ml/common.c

## Purpose
Shared mailing-list support routines for list delivery, membership storage, notifications, and address extraction.

## Main Interfaces
- `getaddrs`: extracts `From`/`Sender` from parsed RFC822 fields.
- `readaddrs`, `addaddr`, `remaddr`, `writeaddr`: maintain append-only address-list files with `!addr` removals.
- `startmailer`: forks `/bin/upas/send` to distribute to all current list members.
- `sendnotification`: sends add/remove notices to subscribers.

## Behavior
Address-list files are append-only and replayed at read time, where comments are ignored and `!` entries remove earlier addresses. `startmailer` sets `upasname` to `<list>-owner` so list mail has a non-empty sender. Membership changes trigger notification unless the address line begins with `#`.

## Dependencies
`common.h`, `dat.h`, Plan 9 `String`, `Biobuf`, `upas/send`, parsed SMTP/RFC822 fields.

## Risks / Notes
Membership uniqueness is exact string equality only. `putenv(smprint(...))` allocations are not reclaimed.
