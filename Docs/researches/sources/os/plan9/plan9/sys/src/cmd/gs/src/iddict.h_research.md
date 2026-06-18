# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iddict.h

Thin dictionary API wrapper that supplies the current interpreter dictionary stack implicitly via `i_ctx_p->dict_stack`.

Defines macros:
- `idict_put`
- `idict_put_string`
- `idict_undef`
- `idict_copy`
- `idict_copy_new`
- `idict_resize`
- `idict_grow`
- `idict_unpack`

Used by operator code that already has `i_ctx_p`.
