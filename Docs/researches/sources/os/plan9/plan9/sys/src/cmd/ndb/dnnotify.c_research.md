# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dnnotify.c

Implements DNS NOTIFY receive and send support for zone changes. `dnnotify()` handles an incoming NOTIFY message, moves the SOA question to the reply, validates that refresh is configured and the question is SOA, checks whether the zone is in a local area, and marks the area for refresh when serials differ.

Outgoing notification is handled by `send_notify()`, which builds an `Onotify` DNS request, resolves slave hostnames to A or AAAA if needed, sends UDP notify packets up to three times, and accepts any matching NOTIFY response. `notify_areas()` sends to all `dnsslave` servers listed on each area SOA and clears `neednotify`.

`notifyproc()` forks a shared-memory background process, marks its `Request` as slave to avoid further subprocess spawning, and wakes every minute to notify updated areas under activity accounting.

Risks include limited validation of responses beyond ID/opcode, synchronous serial comparison against the incoming SOA question, and reliance on `zonerefreshprogram`/area state owned by other modules.
