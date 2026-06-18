# File Research: sources/virtualization/nbdkit/filters/limit/limit.c

Implements a simple concurrent client limit filter. The `limit=` parameter parses an unsigned maximum; `0` disables enforcement. Default limit is `1`.

A global mutex protects the active connection counter. `limit_preconnect()` checks early after passing through to the next preconnect stage, rejecting clients before heavy negotiation when the limit is reached.

`limit_open()` opens the next layer, checks again to prevent slow-negotiation bypass, then increments the counter. `limit_close()` decrements it.

The double check handles the gap between preconnect and open where clients can drop or stall.
