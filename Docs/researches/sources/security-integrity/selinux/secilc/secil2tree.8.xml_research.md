# sources/security-integrity/selinux/secilc/secil2tree.8.xml

Purpose: this DocBook manpage documents the `secil2tree(8)` CIL AST writer. It describes the command as invoking the CIL AST writer for a supplied CIL file and outputting an AST representation.

Important surface: options include `-o/--output`, `-P/--preserve-tunables`, `-Q/--qualified-names`, `-A/--ast-phase`, `-v/--verbose`, and `-h/--help`. Integration points are the generated manpage installation pipeline and cross references to `secilc(8)` and `secil2conf(8)`. It also points users to CIL HTML and PDF reference documentation.

State and persistence: the file is static XML input to manpage tooling; runtime state is represented only as documented command-line flags. Risks: the option list says AST phase must be `parse`, `build`, or `resolve`, while `secil2tree.c` also accepts `post`; documentation can therefore under-specify a real supported mode. It also shows only one plain `file` argument, while the implementation accepts repeated input files. Test signals are documentation build validation, generated manpage inspection, and cross-checks against `secil2tree.c` option parsing.
