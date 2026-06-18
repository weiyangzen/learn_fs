# File Research: sources/os/plan9/9front/sys/src/cmd/upas/ml/common.c

Shared support for simple mailing-list tools.

Key responsibilities:
- Extracts sender addresses from parsed RFC822 header nodes.
- Maintains an in-memory linked list of subscribed addresses.
- Reads append-only address-list files where removals are represented as `!addr`.
- Writes additions/removals to the address-list file and sends notification mail.
- Starts `/bin/upas/send` addressed to all list members.
- Sends subscription/removal notification messages.

Important functions:
- `getaddr()` returns the first parsed address node.
- `getaddrs()` sets globals `from` and `sender`.
- `writeaddr()` appends add/remove records and sends notifications.
- `readaddrs()` applies address-list history into current membership.
- `startmailer()` sets `upasname` to `<list>-bounces` and forks sendmail.
- `sendnotification()` sends owner-style subscription status mail.

Filesystem relevance:
- Address-list file is append-only and permission-adjusted with `DMAPPEND`.
- Mail delivery is delegated to `/bin/upas/send`.

Notable quirks:
- Removal entries do not rewrite the file; history is replayed.
- Notifications are skipped for addresses beginning with `#` on add.
