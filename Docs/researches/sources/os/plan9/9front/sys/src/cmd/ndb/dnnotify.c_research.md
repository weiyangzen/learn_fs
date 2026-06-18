# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dnnotify.c

Implements DNS NOTIFY receive and send support for zone refresh propagation.

Key elements:
- `dnnotify` handles incoming NOTIFY requests by moving the question into the reply, validating SOA type, checking `inmyarea`, and marking the area for refresh when serials differ.
- `getips` resolves slave names to A and AAAA addresses, excluding local interface addresses.
- `send_notify` builds a NOTIFY request with `mkreq`, sends it over UDP up to three times, and waits for an acknowledgement with matching ID/opcode.
- `notify_areas` sends notifications to every `dnsslave` listed in each owned area’s SOA.
- `notifyproc` forks a background process that periodically calls `notify_areas`.

Notable behavior:
- Incoming NOTIFY replies are always formed with `Fresp | Onotify | Fauth`.
- Outgoing notifications use UDP port 53 and include the SOA owner as the question.
- The background process sets `req.isslave = 1` to avoid spawning further resolver slaves.

Risks and quirks:
- `send_notify` passes `Cin` as the second argument to `mkreq`, whose parameter is named `type`; this mirrors existing code but is suspicious because NOTIFY normally asks for SOA.
- `notifyproc` only sends notifications; actual database refresh is coordinated through `needrefresh` and the main activity/aging path.
