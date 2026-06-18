# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/daemon/worker.h

Unbound worker structure and lifecycle interface.

Core types:
- `enum worker_commands`: quit, stats, stats-noreset, remote command, and fast-reload stop/start/poll.
- `struct worker`: thread identity, daemon pointer, command tube, event base, front/back network interfaces, port list, signal handler, command commpoint, stats timer, error rate limiting, random state, allocation cache, per-thread stats, scratch regional, module environment, optional dnstap env, and cache reuse flag.

API:
- create/init/run/delete worker.
- send worker command.
- clear/init worker stats.

Role in group:
- Describes Unbound’s worker execution context used by resolver-side components.
