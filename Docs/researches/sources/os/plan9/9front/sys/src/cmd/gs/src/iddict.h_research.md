# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iddict.h

Provides dictionary API wrappers using the current interpreter dictionary stack.

Key points:
- Defines `idict_stack` as `i_ctx_p->dict_stack`.
- Wraps `dict_put`, `dict_put_string`, `dict_undef`, `dict_copy`, `dict_copy_new`, `dict_resize`, `dict_grow`, and `dict_unpack` with the current dictionary-stack pointer.
- Includes `idict.h` and `icstate.h`.

Research notes:
- This header removes repetitive `&idict_stack` arguments for operator code.
