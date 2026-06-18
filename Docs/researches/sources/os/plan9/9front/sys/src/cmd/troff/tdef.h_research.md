# File Research: sources/os/plan9/9front/sys/src/cmd/troff/tdef.h

This is the core troff definition header. It includes Plan 9 libc/std headers, defines site-dependent paths, device defaults, default point size/font/line length/spacing, output-buffer macros, error macros, and large sets of sizing limits.

It defines troff’s internal `Tchar` representation: motion bits, vertical/negative motion, zero-width bit, font and size fields, character bits, masks, and setters/getters. It also defines internal pseudo-characters for escapes, drawing, X commands, optional hyphens, transparent text, word spaces, and related formatter control states.

The header declares major structs: `Blockp`, `Diver`, `Stack`, `Contab`, `Numtab`, `Wcache`, `Tbuf`, `Env`, `Chwid`, `Font`, `Term`, and `Numerr`. It maps environment fields through macros like `lss`, `font`, `word`, and `line`, making this the shared ABI between most troff implementation files.
