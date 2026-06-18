# sources/security-integrity/selinux/secilc/secilcheck.8.xml

Purpose: this DocBook manpage documents `secilcheck(8)`, a utility for checking a binary SELinux policy against CIL neverallow files.

Important surface: the synopsis requires one binary policy followed by one or more CIL files. Options are `-Q/--qualified-names`, `-m/--multiple-decls`, `-v/--verbose`, and `-h/--help`. It integrates with manpage generation and references `secilc(8)`, `secil2tree(8)`, and `secil2conf(8)`.

State and persistence: the command is documented as a checker; no persistent output is expected besides diagnostics and exit status. Dependencies are external documentation for the CIL language. Risks: spelling and behavior must track `secilcheck.c`; the XML describes `file` arguments generically, so users need examples elsewhere to understand that these are CIL neverallow sources. Test signals should include manpage generation, option parity against `getopt_long`, and CLI examples that assert nonzero exit on violations.
