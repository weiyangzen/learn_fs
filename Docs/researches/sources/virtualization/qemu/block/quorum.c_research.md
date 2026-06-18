# File Research: sources/virtualization/qemu/block/quorum.c

Implements the `quorum` block filter, which presents multiple children as one device and requires a configured vote threshold for reads/writes. It supports normal quorum reads, FIFO reads, blkverify-like two-child comparison mode, optional rewrite of corrupted replicas after a successful read vote, dynamic child add/remove, and QAPI event reporting for bad children or quorum failure.

Reads in quorum mode allocate per-child aligned buffers, launch child read coroutines, collect successes/errors, compare successful data, and either copy the unanimous buffer or compute SHA-256 vote groups to select the winning version. Failed children and losing data versions are reported with `QUORUM_REPORT_BAD`; inability to reach the threshold emits `QUORUM_FAILURE`. If `rewrite-corrupted` is enabled, losing replicas are asynchronously rewritten with the winning data.

Writes and write-zeroes are mirrored to all children. The operation succeeds only if at least `threshold` children complete successfully; otherwise the most common error code is returned. Flush similarly votes over child flush results. `quorum_co_getlength()` requires all children to report the same length.

Open parses `children[]`, `vote-threshold`, `blkverify`, `rewrite-corrupted`, and `read-pattern`. It validates threshold bounds, restricts blkverify to exactly two children with threshold two, opens children as data children, and computes supported zero flags as the intersection of child capabilities. Child permissions request writes only when corrupted-rewrite is enabled and avoid sharing write/resize in ways that could let children diverge. Block status reports zero only when all children report zero for the region.
