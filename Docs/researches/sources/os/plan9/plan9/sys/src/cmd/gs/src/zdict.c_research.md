# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdict.c

Implements core PostScript dictionary operators.

Core operators include `dict`, `maxlength`, `begin`, `end`, `def`, `load`, `.undef`, `known`, `where`, `currentdict`, `countdictstack`, `dictstack`, and `cleardictstack`.

`zop_def()` is a performance-sensitive helper used by `def`. It fast-paths top-dictionary name redefinition with single-probe lookup, combines writable dictionary and store checks, and falls back to `idict_put()` when necessary.

`zload()` fast-paths name lookup through the dictionary stack, while non-name keys are searched explicitly with read checks on each dictionary.

`zcopy_dict()` implements dictionary copy behavior, including Level 1 access-attribute compatibility and dictionary auto-expand behavior.

Extensions include `.dictcopynew`, `.dicttomark`, `.forceundef`, `.knownget`, `.knownundef`, and `.setmaxlength`.

Operator definitions are split into `zdict1_op_defs` and `zdict2_op_defs`.
