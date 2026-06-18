# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iapriocntl.h

## Role

`iapriocntl.h` defines the interactive scheduling class ABI for `priocntl(2)` and `dispadmin(8)`.

## Key Interfaces and Data

- `iaparms_t` carries user priority limit, user priority, and interactive mode. Its beginning must match `tsparms` for interchangeability.
- `iaclass_t` stores class ID and class parameters.
- `iainfo_t` reports maximum configured user priority.
- Constants define no-change sentinel, max/off user priority, process count, interactive off/on mode values, and boost amount.
- Varargs keys are `IA_KY_UPRILIM`, `IA_KY_UPRI`, and `IA_KY_MODE`.
- `iaadmin_t` points to `iadpent` table entries and carries count/command.
- `_SYSCALL32` defines `iaadmin32_t` for ILP32 callers.
- Admin commands are `IA_GETDPSIZE`, `IA_GETDPTBL`, and `IA_SETDPTBL`.

## Dependencies and Use

This ABI header pairs with kernel scheduler internals in `ia.h` and shares `iadpent` table layout.

## Research Notes

The explicit `tsparms` prefix compatibility is important for callers or code paths that treat interactive and time-sharing parameters polymorphically.
