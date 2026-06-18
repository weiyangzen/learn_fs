# sources/security-integrity/selinux/secilc/secil2tree.c

Purpose: `secil2tree` loads CIL source files into a libcil database and writes one of several AST views. It is a diagnostic/developer utility rather than a binary policy compiler.

Important APIs and flow: `enum write_ast_phase` models parse, build, resolve, and post phases. Option parsing supports `-o`, `-P`, `-Q`, `-A`, `-v`, and `-h`; phase names are parsed with `strcasecmp`. The program initializes `cil_db`, sets tunable and qualified-name behavior, disables attribute expansion, reads every input into memory, adds it via `cil_add_file`, then chooses `cil_write_parse_ast`, `cil_write_build_ast`, `cil_write_resolve_ast`, or `cil_write_post_ast`. Unlike `secilc`, it does not explicitly call `cil_compile`; the selected writer drives the relevant internal CIL phases.

State and persistence: output is stdout by default or the path passed to `-o`; CIL state is transient. Dependencies are libsepol/libcil and standard file APIs. Risks: repeated `-o` leaks earlier `output` strings, empty files have the same `malloc(0)`/`fread` edge risk as `secil2conf`, and the manpage omits the `post` phase. Test signals should cover all AST phases, repeated input files, stdout versus file output, invalid phase names, and option/manpage parity.
