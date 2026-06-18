# File Research: sources/os/plan9/9front/sys/src/cmd/upas/ml/mlowner.c

Owner-command processor for list subscription requests.

Key responsibilities:
- Reads a delivered message from stdin.
- Parses headers to identify `From` or `Sender`.
- Searches message text for subscription keywords.
- Appends remove or subscribe records to the address-list file.

Important behavior:
- If message contains `remove` or `unsubscribe`, calls `writeaddr(..., rem=1)`.
- Else if it contains `subscribe`, calls `writeaddr(..., rem=0)`.

Filesystem relevance:
- Mutates the append-only list address file through shared `writeaddr()`.

Notable constraints:
- Reads only first 128 KiB after the Unix `From ` line.
- Keyword matching is plain substring matching over the whole buffered message.
