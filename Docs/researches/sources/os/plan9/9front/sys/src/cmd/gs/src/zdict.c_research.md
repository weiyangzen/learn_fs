# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdict.c

Implements PostScript dictionary and dictionary-stack operators.

Key behavior:
- Provides `dict`, `maxlength`, `begin`, `end`, `def`, `load`, `.undef`/`undef`, `known`, `where`, dictionary `copy`, `currentdict`, `countdictstack`, `dictstack`, and `cleardictstack`.
- `zop_def` has a fast path for redefining named keys in the top dictionary while combining write/access/store checks.
- `zload` uses fast name lookup for names and explicit dictionary-stack iteration for other key types.
- Level 2/extensions include `.dictcopynew`, `.dicttomark`, `.forceundef`, `.knownget`, `.knownundef`, and `.setmaxlength`.
- `zdicttomark` builds a dictionary from mark-delimited key/value pairs in top-to-bottom order to preserve duplicate-key behavior.

Dependencies:
- Uses dictionary internals, dictionary-stack macros, packed/name lookup helpers, VM-space/store checks, and level-mode flags.

Research notes:
- This is performance-sensitive interpreter infrastructure. Store checks and top-dictionary fast paths are central to safe mutation.
