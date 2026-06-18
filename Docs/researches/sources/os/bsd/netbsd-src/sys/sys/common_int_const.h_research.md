# File Research: sources/os/bsd/netbsd-src/sys/sys/common_int_const.h

## Scope

Defines C99 integer constant macros for fixed-width, least/fast-width, and max-width integer types.

## APIs And Behavior

- Requires compiler integer constant suffix macros.
- Uses token-pasting helpers to append suffixes.
- Defines `INT8_C`, `INT16_C`, `INT32_C`, `INT64_C`, `UINT8_C`, `UINT16_C`, `UINT32_C`, `UINT64_C`, `INTMAX_C`, and `UINTMAX_C`.

## Dependencies

- Relies on compiler-provided `__INT*_C_SUFFIX__`, `__UINT*_C_SUFFIX__`, and max suffix macros.

## Risks And Invariants

- Incorrect suffix macros would produce constants with wrong type/rank.
- Header intentionally only defines constant macros, not typedefs.
