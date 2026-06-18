# File Research: sources/virtualization/spdk/module/event/subsystems/keyring/Makefile

Builds the event keyring subsystem library.

Key elements:
- Compiles `keyring.c`.
- Produces `event_keyring`.
- Uses shared object version `3.0`.
- Uses the blank SPDK map file.

Dependencies:
- Built via standard SPDK library make infrastructure.

Research notes:
- Separate backend keyring modules live under `module/keyring`.
