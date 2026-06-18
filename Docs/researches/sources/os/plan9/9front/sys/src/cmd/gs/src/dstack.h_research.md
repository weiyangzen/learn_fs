# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dstack.h

## Role
Ghostscript interpreter header defining dictionary-stack access macros and documenting dictionary lookup/cache design.

## Contents
- Includes `idstack.h` and `icstate.h`.
- Maps interpreter context fields to short dictionary-stack macros such as `idict_stack`, `d_stack`, `dsbot`, `dsp`, and `dstop`.
- Defines interpreter-specific wrappers around generic dstack APIs for name lookup, permanent dictionary tests, GC cleanup, and top-of-stack cache maintenance.
- Defines `check_dstack(n)` to fail with `e_dictstackoverflow` if the current block lacks room.
- Contains a long design note on dictionary lookup performance, current caching behavior, and a proposed improved cache/restoration-stack design.

## Important Interfaces
- Macros: `dict_find_name_by_index`, `dict_find_name`, `dict_find_name_by_index_inline`, `if_dict_find_name_by_index_top`.
- Stack/cache macros: `dict_set_top`, `dict_is_permanent_on_dstack`, `dicts_gc_cleanup`, `systemdict`.
- Safety macro: `check_dstack`.

## Dependencies And Coupling
- Tightly coupled to interpreter context variable `i_ctx_p`, `dict_stack` shape, Ghostscript ref spaces, and error constants.
- Assumes dictionary stack is a linked list of blocks and warns that full-stack operations must not only inspect the top block.

## Risks And Notes
- Mostly macro API, so misuse can cause hidden control flow (`return_error`) and context-dependent side effects.
- Comments describe an improved design but not all behavior is implemented in this header; treat notes as architecture context rather than active code.

## Filesystem Relevance
None directly. This is language interpreter state management inside the vendored Ghostscript tree.
