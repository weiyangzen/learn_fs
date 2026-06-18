# File Research: sources/os/plan9/plan9/sys/src/9/ip/ipmux.c

Implements a packet filter/demultiplexer protocol that can intercept IP packets before normal protocol dispatch.

Key responsibilities:
- Parses semicolon-separated filter expressions such as `proto=17`, `src=...`, `dst=...`, `ifc=...`, `iph[...]`, and `data[...]`, with optional masks and value alternatives.
- Represents filters as ordered decision trees (`Ipmux`) with yes/no branches, comparison type specialization, masks, values, refcounts, and target conversations.
- Canonicalizes filter chains by field type, offset, length, and mask specificity.
- Merges new filters into the global demux tree and removes them on close.
- `ipmuxconnect` installs a filter tree and connects the conversation.
- `ipmuxiput` evaluates inbound packets against installed filters; matching packets are delivered to the conversation with interface address prepended. Nonmatching packets fall back to normal protocol dispatch via `t2p`.
- `ipmuxkick` sends fully formed IPv4 or IPv6 packets written by users back down the stack.
- `ipmuxstate` and `ipmuxstats` print installed filter trees.

Notable constraints:
- Comments note no protection against overlapping specs.
- Filtering is heavily IPv4-header oriented, though output dispatch can handle IPv6 by version.
