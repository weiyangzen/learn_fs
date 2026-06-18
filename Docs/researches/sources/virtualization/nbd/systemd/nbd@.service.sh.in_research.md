# File Research: sources/virtualization/nbd/systemd/nbd@.service.sh.in

## Purpose
Shell template that emits a parameterized systemd unit for managing an NBD client connection for a device instance.

## Behavior
Expands Autoconf variables for prefix paths, then prints a unit with:
- `Description=NBD client connection for %i`
- `PartOf=nbd.service`
- startup before `dev-%i.device` and after `network-online.target`
- oneshot service with `RemainAfterExit=yes`
- `ExecStart=@sbindir@/nbd-client %i`
- `ExecStop=@sbindir@/nbd-client -d /dev/%i`
- install requirements for the base NBD device and partitions `p1` through `p15`

## Dependencies
Requires Autoconf substitution and a shell capable of here-documents.

## Risks and Notes
The generated unit assumes `%i` maps correctly to both `nbd-client` lookup input and `/dev/%i` disconnect path.
