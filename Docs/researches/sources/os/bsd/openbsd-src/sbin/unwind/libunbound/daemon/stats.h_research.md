# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/daemon/stats.h

Unbound daemon statistics interface.

API:
- Initialize `ub_server_stats` from config.
- Record cache misses and prefetches.
- Log stats per worker/thread.
- Obtain stats from another worker through command pipe.
- Compile/reset stats for a worker.
- Reply with stats over worker communication.
- Add stats blocks together.
- Insert query metadata, rcode, and downstream DNS Cookie stats.

Role in group:
- Stats contract used by Unbound workers and remote-control/reporting paths.
