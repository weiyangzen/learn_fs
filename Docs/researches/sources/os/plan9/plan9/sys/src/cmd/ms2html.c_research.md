# File Research: sources/os/plan9/plan9/sys/src/cmd/ms2html.c

Single-file converter from troff/ms input to HTML.

Major responsibilities:
- Reads input from stdin with nested `.so` include support.
- Expands troff strings, number registers, macros, macro arguments, and conditionals.
- Translates many ms/troff macros into old-style HTML tags.
- Converts special characters/entities and troff escapes.
- Generates auxiliary GIFs for equation/table/picture blocks via `troff2gif` and PostScript pictures via `ps2gif`.

Key data:
- Macro dispatch tables `gtab` and `gtabif`.
- Entity mapping table for HTML/numeric entities and Unicode runes.
- Troff special-character mapping table `tspec`.
- Font stack for `<B>`, `<I>`, `<TT>`, and mixed fonts.
- String/number-register/macro linked lists.
- Source stack for includes, string stack, and macro expansion stack.

Important functions:
- `doconvert()` main conversion loop, prints `<html>`, dispatches directives at line start, emits body text, closes open structures.
- `getrune()` and `getnext()` provide logical input with string/macro expansion and escape translation.
- `dodirective()` parses directive lines, invokes user macros, conditional handlers, or built-in macro handlers.
- `copyline`, `copyarg`, `parseargs` parse directive arguments.
- `g_PP`, `g_LP`, `g_IP`, `g_SH`, `g_NH`, `g_TL`, font handlers, list handlers, quote/display handlers map ms constructs to HTML.
- `g_de`/`g_rm` define/remove macros.
- `g_ds`/`g_as` define/append strings; `g_nr` sets number registers.
- `g_if`, `g_ie`, `g_el` evaluate conditional bodies.
- `g_startgif()` captures `EQ`, `TS`, `PS` blocks and invokes `troff2gif`.
- `g_BP()` embeds GIF/JPEG directly or converts other pictures through `ps2gif`.

Behavior notes:
- Uses old HTML tags such as `<DL>`, `<TT>`, `<PRE>`, `<center>`.
- `quiet` defaults to suppress ignored-macro warnings; `-q` turns warnings on by setting `quiet = 0`.
- Always appends an Alcatel-Lucent copyright footer.
- Conditional arithmetic supports simple integer operators and comparisons.
- Some handlers are intentionally ignored or “not yet supported.”
