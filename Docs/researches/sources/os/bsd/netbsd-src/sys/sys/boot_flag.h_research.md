# File Research: sources/os/bsd/netbsd-src/sys/sys/boot_flag.h

## Scope

Defines a macro for translating single-character boot arguments into reboot/autoboot flags.

## APIs And Behavior

- `BOOT_FLAG(arg, retval)` switches on characters and ORs known flags into `retval`.
- Recognizes machine-dependent `1` through `4` as `RB_MD1` through `RB_MD4`.
- Recognizes `a`, `b`, `c`, `d`, `m`, `q`, `s`, `v`, `x`, and `z` for askname, halt, userconf, debugger, miniroot, quiet, single-user, verbose, debug, and silent boot modes.
- Unknown characters leave `retval` unchanged.

## Dependencies

- Includes `sys/reboot.h` for `RB_*` and `AB_*` constants.

## Risks And Invariants

- Ports may not implement every recognized flag.
- Macro mutates its `retval` argument and should be passed an lvalue without side effects.
