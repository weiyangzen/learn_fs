# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/ni.c

Global data definitions and built-in request table for troff/nroff.

Key responsibilities:
- Defines terminal/font directory strings, default device name, initial number registers, page-range globals, output globals, input globals, environment arrays, diversion arrays, special-character ids, and indirect function pointers.
- Defines the built-in `contab[]` mapping request names to handler functions.
- Provides the initial environment `env[0]`.
- Defines special-name mappings such as hyphen, em dash, rule, minus, ligatures, accents, underline, root extender, box rule, and dagger.
- Defines global state for macro stacks, pushback, traps, line layout, hyphenation, output motion, and device mode.

Important behavior:
- Request names are two-character packed names created by `PAIR`.
- `mnspace()` copies `contab[]` into dynamic `contabp` during initialization.
- The indirect function pointers are assigned by troff or nroff device initialization.

Notable risks:
- This is the storage anchor for most globals declared in `ext.h`.
- Any request table change affects parser dispatch and macro-name collision behavior.
- The program depends on the initial environment values matching historical troff defaults.
