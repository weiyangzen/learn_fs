# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/main.c

This is the eqn command driver. It parses options, initializes device and symbol tables, reads input files, detects display and inline equations, runs the parser, and emits troff output.

Key responsibilities:
- Handles options for delimiters/debug, size, sub/sup size delta, minimum size, font, no-output equations, and typesetter.
- Initializes the typesetter with `settype`.
- Reads each input stream through `getdata`.
- Detects `.EQ`/`.EN` display equations and inline delimiter equations.
- Runs `yyparse` for equation bodies.
- Emits final equation strings, height spacing, `.lf` line synchronization, and mark/lineup support.
- Manages string-register allocation with `salloc`/`sfree`.
- Converts point sizes and em units with `ABSPS`, `DPS`, `EFFPS`, `EM`, and `REL`.

Important implementation notes:
- Inline equations accumulate surrounding text and equation fragments into a temporary string register.
- `putout` adds vertical spacing before/after equations when needed and clears `spaceval`.
- Register IDs 11-99 are available for equation strings.
