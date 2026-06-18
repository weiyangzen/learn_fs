# File Research: sources/os/plan9/9front/sys/src/cmd/upas/ml/mlmgr.c

Mailing-list management command for creating lists and adding/removing members.

Key responsibilities:
- Creates list, owner, and bounces mailboxes for `-c`.
- Creates `pipeto` scripts for list delivery, owner commands, and bounce sink.
- Adds or removes addresses by appending records to the list address file.
- Handles optional domain in `listname@domain` for reply-to flag generation.

Important functions:
- `createpipeto()` writes executable rc scripts into each mailbox’s `pipeto`.
- `main()` enforces mutually exclusive `-c`, `-a`, and `-r`.

Filesystem relevance:
- Creates mailboxes with `creatembox()`.
- Writes mailbox `pipeto` files and address-list file under mailbox paths.
- Sets executable-ish mode on `pipeto`.

Notable quirks:
- Bounces mailbox `pipeto` script simply exits successfully.
- Writes marker comments to address-list file before management operations.
