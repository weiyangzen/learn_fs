# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_queue.c

`pfctl_queue.c` implements queue display and live queue statistics formatting for `pfctl -s queue`. It fetches queue specs/stats from the PF kernel, maintains a local list keyed by queue name and interface, computes moving averages, and prints HFSC/FQ-CoDel related counters.

Primary responsibilities:
- Defines `struct queue_stats`, containing either HFSC class stats or FQ-CoDel stats, moving-average state, and previous byte/packet counters.
- Defines `struct pfctl_queue_node`, tying a `pf_queuespec` to current stats in the global `qnodes` list.
- Implements `pfctl_show_queues()` as the public display entry point.
- Implements `pfctl_update_qstats()` to fetch all queues and refresh or insert local nodes.
- Implements display helpers for queue specs, verbose stats, debug ids, measured rates, and FQ-CoDel delay stats.
- Implements `rate2str()` for human-readable bit-rate formatting.

Control flow:
- `pfctl_show_queues()` calls `pfctl_update_qstats()`, optionally prints a title, filters by interface, and prints each queue.
- With second-level verbosity (`verbose2`), it loops every `STAT_INTERVAL` seconds, refreshes stats, and reprints measured rates until interrupted or an update fails.
- `pfctl_update_qstats()` first calls `DIOCGETQUEUES` to get count/ticket. A ticket change resets the cached queue-node list. It then iterates with `DIOCGETQSTATS`.
- Existing nodes preserve moving-average history; new nodes are inserted and initialized.

Integration points:
- Called by `pfctl.c` show dispatch.
- Uses `print_queuespec()` from `pfctl_parser.c` for base queue rendering.
- Depends on kernel queue/stat structs from `<net/pfvar.h>`, `<net/hfsc.h>`, and `<net/fq_codel.h>`.
- Uses `PF_OPT_VERBOSE`, `PF_OPT_DEBUG`, and `PF_OPT_SHOWALL` option flags from shared headers.

Notable risks and edge cases:
- Queue-node storage is process-lifetime oriented; nodes are removed from the TAILQ but not explicitly freed before process exit.
- The stats union is interpreted as HFSC for generic packet/byte/drop fields and as FQ-CoDel for flow delay fields when queue flags indicate a top-level flow queue.
- Moving average only updates when counters are monotonic; counter resets/ticket changes clear node state.
