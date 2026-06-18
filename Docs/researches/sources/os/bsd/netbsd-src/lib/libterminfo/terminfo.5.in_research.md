# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/terminfo.5.in

Manual page template for `terminfo(5)`.

Key contents:
- Describes terminfo source syntax:
  - comma-separated fields,
  - header line with names/aliases/description,
  - boolean/numeric/string capabilities,
  - comments and whitespace,
  - escape sequences,
  - delay syntax.
- Documents parameterized string `%` operations, including stack operations, variables, arithmetic, conditionals, and string formatting.
- Contains placeholders for generated capability tables:
  - `@BOOLCAPS@`
  - `@NUMCAPS@`
  - `@STRCAPS@`
- Includes a sample `vt100`-style entry.
- Documents compiled database lookup behavior:
  - cdb-backed databases,
  - `$TERMINFO`,
  - `$TERMCAP`,
  - `$HOME/.terminfo`,
  - `/usr/share/misc/terminfo`,
  - embedded fallback terms.
- Notes compatibility difference for `TERMINFO_DIRS` versus ncurses.

Role in subsystem:
- Source template for generated `terminfo.5`, with tables populated by `genman`.
