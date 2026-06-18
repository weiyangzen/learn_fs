# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lapi.h

## Role

`lapi.h` provides small internal helpers used by the Lua API implementation.

## Main Responsibilities

- Defines `api_incr_top(L)`, which advances the Lua stack top and checks against the active call frame limit.
- Defines `adjustresults(L,nres)`, which expands the current call frame top for `LUA_MULTRET` results.
- Defines `api_checknelems(L,n)`, which validates that enough API stack elements exist for an operation.

## Integration Points

It includes `llimits.h` and `lstate.h`, and is consumed by API and call-path files such as `lapi.c` and `ldo.c`.

## Risk Notes

These macros are small but central to stack discipline. Bugs here affect nearly every public API operation.
