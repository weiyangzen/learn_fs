# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/engine.h

## Purpose
`engine.h` declares the engine process entry point and the main-process configuration message used when applying a lease.

## Exports
- `struct imsg_configure_interface`: fixed-size payload carrying interface index, rdomain, IPv4 address, mask, next-server address, boot file, domain name, hostname, routes, and route count.
- `engine(int, int)`: starts the engine process.
- `engine_imsg_compose_frontend(int, pid_t, void *, uint16_t)`: sends an imsg from engine to frontend.

## Integration Notes
The large string buffers are sized for `vis(3)` expansion of DHCP fields before crossing process boundaries.
