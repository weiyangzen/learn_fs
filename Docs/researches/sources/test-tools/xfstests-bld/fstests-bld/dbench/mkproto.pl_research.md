<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/mkproto.pl -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/mkproto.pl

Source read: complete file, 112 lines, 2174 bytes, sha256 `bde40ab154569441127efa032dd8b658c5214665858a02147f3207b8cd96088c`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/mkproto.pl_research.md`.

Purpose: Perl prototype generator used by `make proto` to produce `proto.h` from C source files. It is inherited from Samba-style tooling and emits public function declarations grouped by source filename.

Important APIs/types/functions: `-h HEADER_GUARD` overrides the default `_PROTO_H_`; `print_header()` and `print_footer()` write include guards; `process_file()` scans one source file; `handle_loadparm()` expands `FN_GLOBAL_*` and `FN_LOCAL_*` macro declarations into accessor prototypes; `process_files()` applies the scanner to all arguments.

Control flow: for each file, it prints a comment header, skips indented lines, non-function-looking lines, comments, semicolon declarations, and `main()`, then matches allowed return-type prefixes. Single-line function signatures ending in `)` get a semicolon; multi-line signatures are printed until a line ending in `)` is reached.

State and persistence behavior: no persistent state beyond generated stdout. It reads listed source files and exits on open failure. The generated header content depends on input order, so build rules must pass sources deterministically.

Dependencies and integration: requires Perl with `strict` but intentionally avoids `warnings` for old portability. Integrates with the dbench build system to regenerate `proto.h`, and its return-type whitelist includes many Samba-era typedefs beyond this small dbench tree.

Risks: regex parsing is approximate and can miss static/indented declarations, emit malformed prototypes for unusual formatting, or duplicate symbols from mutually exclusive backends such as `fileio.c` and `sockio.c`. It does not parse C comments robustly and assumes prototype-worthy signatures start at column zero.

Test signals: run `make proto` and compare the generated `proto.h` with the checked-in version. Add edge-case source snippets only if changing function formatting or return types.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/mkproto.pl -->
