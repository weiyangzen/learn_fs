# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/dump_net_stats.h

## Role

This header defines the o2net stats record used by the debugfs network statistics command.

## Data Model

`struct net_stats` stores validity, send count, acquire/send/wait timing totals, receive count, and processing-time total for one node.

## API

It declares `dump_net_stats(FILE *out, char *path, int interval, int count)` for single-shot or repeated network-stat dumps.
