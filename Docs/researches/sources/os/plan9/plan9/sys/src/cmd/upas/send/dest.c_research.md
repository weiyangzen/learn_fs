# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/dest.c

## Purpose
Destination list data structure helpers for `upas/send`.

## Main Interfaces
- `d_new`, `d_free`: destination allocation.
- `d_insert`, `d_rm`: circular queue management.
- `d_same_insert`, `d_rm_same`: group equivalent destinations for one command/mailbox.
- `d_to`: generate a `To:` header from destinations.
- `s_to_dest`: parse whitespace/quote-separated destination strings.

## Behavior
Destinations are stored as circular lists; `same` chains group destinations with identical delivery action/replacement while suppressing duplicates and limiting group size/argument length.

## Dependencies
`String`, destination status definitions, escaping helpers.

## Risks / Notes
Parsing is whitespace-oriented with basic double-quote handling, not full RFC822 address parsing.
