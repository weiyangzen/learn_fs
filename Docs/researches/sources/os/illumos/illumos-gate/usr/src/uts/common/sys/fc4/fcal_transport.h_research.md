# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fcal_transport.h

## Role

`fcal_transport.h` defines FC-AL transport packet and operation vectors used by FC-AL upper-layer protocol drivers and SOCAL-style adapters.

## Packet And Transport Structures

- Defines `fc_devdata_t`, `fc_ioclass_t`, `fcal_sleep_t`, `fc_iotype_t`, and `fc_uc_cookie_t`.
- `fcal_packet_t` stores adapter cookie, next pointer, completion/private data, flags, command state, transport/diagnostic status, SOC request union, response header, magic, and command count.
- Packet flags include no-interrupt, complete, response-header-valid, aborting, and aborted.
- Command state bits include in-transport, complete, and completion-called.
- `fcal_transport_t` carries adapter handle, DMA limits/attributes, access attributes, login parameters, node/port WWNs, port number, command maximum, lock/cv, and operation table.

## Operations And Status

`fcal_transport_ops_t` includes submit, poll submit, LILP map, force LIP, abort command, ELS request, bypass device, force reset, add/remove upper-layer protocol, and take-core hooks.

Return/status constants cover success, timeout, allocation failure, old port, link error, offline, aborted, abort failure, bad abort/params, overrun, no transport, transport failure/unavailable/queue-full/timeout, login pseudo-statuses, and generic `FCAL_FAILURE`.

Defines FC-AL state reset value, LILP map magic/bad-magic, LIP request constants, and `fcal_lilp_map_t` with AL_PA list.
