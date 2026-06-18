# File Research: sources/os/bsd/netbsd-src/lib/libedit/map.h

## Purpose
Private header for editor key-map state and operations.

## Main Declarations
- `el_func_t`: editor command function pointer type.
- `el_bindings_t`: command ID, user-visible name, and description for bind/help output.
- `el_map_t`: per-`EditLine` key-map state including normal/alternate/current maps, static defaults, help/function arrays, mode type, and word characters.
- Mode constants `MAP_EMACS`, `MAP_VI`; key table size `N_KEYS`.

## Integration
Used by `map.c`, `read.c`, command implementations, and `EditLine` state in `el.h`.

## Risks And Notes
The header exposes the private shape of the key-map subsystem. Any change to `el_map_t` affects `EditLine` allocation/lifecycle and all command-dispatch code.
