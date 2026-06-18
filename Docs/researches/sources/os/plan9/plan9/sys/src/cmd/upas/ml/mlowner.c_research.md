# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/ml/mlowner.c

## Purpose
Owner-command processor for mailing-list subscribe/unsubscribe requests.

## Behavior
Reads one message from stdin, discards Unix `From `, reads up to 128 KiB, parses headers, extracts sender, then removes the sender if the message contains `remove` or `unsubscribe`, or adds the sender if it contains `subscribe`.

## Dependencies
Mailing-list common helpers, SMTP/RFC822 parser.

## Risks / Notes
Command detection is a raw substring search over the message; “unsubscribe” also contains “subscribe”, but removal is checked first.
