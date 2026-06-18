# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ztrap.c

## Purpose
Provides minimal trapping-parameter operator support for LanguageLevel 3 trapping features.

## Public Surface
- `.settrapparams`: reads a dictionary and applies it to `i_trap_params`.
- `settrapzone`: registered but not implemented, returns `undefined`.
- Registered through `ztrap_op_defs`.

## Implementation Notes
- Defines global `gs_trap_params_t i_trap_params` with a source comment marking the design as questionable.
- `.settrapparams` wraps a dictionary as a `dict_param_list`, calls `gs_settrapparams`, releases the parameter list, and pops on success.

## Dependencies
Uses dictionary parameter-list parsing and graphics trapping APIs from `gstrap.h`.

## Risks and Notes
- `settrapzone` is explicitly NYI.
- Global trap parameter storage is called out as bogus by the source.
- Filesystem relevance: none.
