# sources/security-integrity/selinux/secilc/secilc.8.xml

Purpose: this DocBook manpage documents `secilc(8)`, the SELinux CIL compiler that builds a kernel binary policy and a `file_contexts` file from CIL input.

Important surface: it documents output selection (`-o`, `-f`), target platform (`-t selinux|xen`), MLS override, binary policy version, unknown-class handling, dontaudit suppression, tunable preservation, qualified names, multiple declarations, neverallow disabling, generated-attribute expansion, size-based attribute expansion, optimization, verbosity, and help. It integrates with generated manpage installation and references `file_contexts(5)`, `sestatus(8)`, CIL reference docs, and the CIL design wiki.

State and persistence: the documented outputs are the binary policy and file-contexts file. Risks: option spelling in the XML says `--filecontext`, while `secilc.c` registers the long option as `--filecontexts`; it says default policy version depends on the system, but the code defaults to `POLICYDB_VERSION_MAX`. These mismatches can mislead automation and users. Test signals should compare generated manpage options with `getopt_long` definitions and verify documented defaults against actual compiler behavior.
