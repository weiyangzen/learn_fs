# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/init.c

Static initialization and reinitialization ordering for isakmpd subsystems.

`init()` order:
- Application, DOI, exchange, DH group, IPsec, ISAKMP DOI.
- Timer.
- Config and connection, which depend on timer.
- Logging reinit after config.
- Policy after config.
- Cert/CRL after config and policy.
- SA, transport, virtual, UDP, NAT-T, UDP encapsulation, vendor registry.

`reinit()`:
- Logs daemon reinitialization.
- Reloads config, logging, policy, certs, CRLs, connections.
- Reinitializes transports to rescan interfaces.
- Reinitializes SAs.
- Comments note unresolved questions about pending exchange timers and stale last messages after SIGHUP/UI reinit.

This file is the dependency-order anchor for daemon startup rather than a generic module registry.
