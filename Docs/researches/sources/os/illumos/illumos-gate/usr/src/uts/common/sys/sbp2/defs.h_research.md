# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sbp2/defs.h

## Role

SBP-2 wire-protocol definition header. It describes ORB formats, management operations, login/query/reconnect/logout/task-management ORBs, status blocks, command block agent registers, page-table elements, and Config ROM keys.

## Key Elements

- Defines dummy ORB and command ORB structures plus common ORB parameter bits.
- Defines command ORB fields for direction, speed, max payload, page table, and page size.
- Defines management ORB base structure and function codes for login, query logins, reconnect, set password, logout, abort task, abort task set, LUN reset, and target reset.
- Defines specialized login, query-logins, reconnect, logout, and task-management ORB structures.
- Defines login response layout, including login ID and command agent address.
- Defines `sbp2_status_t` and status parameter fields for source, response, dead bit, length, SBP status, failed object, and serial bus error.
- Defines command block agent register offsets and agent states.
- Defines unrestricted page table element layout and max segment size.
- Defines Config ROM key type/value constants for management agent, LUN, and unit characteristics.
- Defines LUN and unit-characteristic bit masks.

## Dependencies and Coupling

Includes `sbp2/common.h` for address and ORB pointer types. Warlock annotations mark protocol structures as unique per ORB.

## Research Notes

The file is a direct translation of ANSI NCITS 325-1998 SBP-2 protocol layout. It avoids implementation policy except for constants needed by the driver layer.
