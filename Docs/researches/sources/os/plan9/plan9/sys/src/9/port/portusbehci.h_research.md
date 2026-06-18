# File Research: sources/os/plan9/plan9/sys/src/9/port/portusbehci.h

Defines portable EHCI USB host-controller register layouts and bit constants.

Contents:
- `Ecapio`: EHCI capability registers: `cap`, `parms`, `capparms`, `portroute`.
- `Edbgio`: EHCI debug port registers: `csw`, `pid`, 8-byte `data`, and `addr`.
- Capability bits for port count, debug port index, 64-bit support, programmable frame list, async park, and extended capability pointer.
- Legacy support register offsets/ids.
- Typed queue link constants for EHCI schedule entries.
- Command/status/interrupt/config/port-status bit definitions.
- Debug port control/status, PID, toggle, device address, and endpoint bit definitions.

Role:
- Header-only hardware contract consumed by EHCI controller/debug-port code.
