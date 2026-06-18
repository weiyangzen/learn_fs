# sources/user-network-fs/samba/source3/printing/load.h

## Purpose
`load.h` is the public header for printer-loading helpers implemented in `load.c`.

## Important APIs, types, and functions
- `bool pcap_cache_loaded(time_t *_last_change);` checks whether the printer cache is available and can return its last refresh time.
- `void load_printers(void);` loads automatic and cached printer services into Samba's loadparm state.

## Control flow
The header only declares functions. Callers include it when they need to trigger printer service loading or inspect pcap cache state.

## State and persistence behavior
No state is stored in the header. The declared functions interact with loadparm and printer-list state in `load.c`.

## Dependencies and integration points
The prototypes expose the printing load component to source3 code. Including files must already have Samba's common types available for `bool` and `time_t`.

## Risks and edge cases
The header is minimal; main risk is ABI/API drift if `load.c` signatures change without updating this declaration or generated include users.

## Test signals
Compile coverage is the primary signal: any caller using stale declarations will fail to build. Runtime behavior is covered by `load.c` tests.
