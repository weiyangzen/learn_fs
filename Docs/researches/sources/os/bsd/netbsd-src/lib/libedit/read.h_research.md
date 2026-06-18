# File Research: sources/os/bsd/netbsd-src/lib/libedit/read.h

## Purpose
Private declarations for the input-reading subsystem.

## Main Declarations
- `read_init`
- `read_end`
- `read_prepare`
- `read_finish`
- `el_read_setfn`
- `el_read_getfn`

## Integration
The public `el_gets`/`el_wgets` stack and readline compatibility layer depend on these functions to install custom readers and maintain terminal state.

## Risks And Notes
The `struct el_read_t` type is opaque in this header; users must interact through the declared helper functions.
