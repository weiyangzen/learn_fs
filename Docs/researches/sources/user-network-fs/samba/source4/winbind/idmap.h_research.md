<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/winbind/idmap.h -->
# sources/user-network-fs/samba/source4/winbind/idmap.h

## Purpose

This header defines the Samba4 winbind idmap context and exposes generated idmap prototypes.

## Important APIs, Types, and Functions

- `struct idmap_context` contains `lp_ctx`, `ldb_ctx` for `idmap.ldb`, and `samdb` for `sam.ldb`.
- It forward-declares `struct tevent_context`.
- It includes `winbind/idmap_proto.h`, generated from `idmap.c`.

## Control Flow

No executable flow exists. Callers include this header, initialize `idmap_context` with `idmap_init()`, and use generated prototypes for mapping functions.

## State and Persistence Behavior

The context holds handles to persistent databases but does not itself manage persistence beyond talloc lifetime. Freeing the context closes associated LDB handles.

## Dependencies and Integration Points

It includes generated ID mapping types from `librpc/gen_ndr/idmap.h` and is used by Samba4 winbind/idmap consumers.

## Risks and Edge Cases

The structure exposes database internals directly, so callers can bypass intended mapping APIs if they include this header. Generated prototype availability depends on the Waf `autoproto` step.

## Test Signals

Build success for idmap consumers and correct generation of `idmap_proto.h` are the main signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/winbind/idmap.h -->
