# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idsdata.h

Defines `dict_stack_t`, the dictionary stack state.

Fields:
- underlying `ref_stack_t`
- `min_size`
- `userdict_index`
- `def_space` cache for fast `def` legality
- `top_keys`, `top_npairs`, `top_values` cache for fast top-dictionary lookup
- cached `system_dict`

It documents Level 1/Level 2 handling of `globaldict` by replacing it with a systemdict copy rather than physically changing minimum stack size.
