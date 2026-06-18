# sources/security-integrity/selinux/secilc/docs/Makefile
# sources/security-integrity/selinux/secilc/docs/Makefile

Purpose: builds CIL reference guide HTML and PDF from Markdown sources and syntax-highlighting definition.

Important APIs and control flow: lists all guide Markdown files, copies them to `tmp/`, rewrites internal markdown links for PDF conversion with `sed`/`gsed`, wraps `../test/policy.cil` in a Markdown code fence, and runs `pandoc` with `secil.xml` syntax definition to generate standalone HTML and PDF outputs. `clean` removes html/pdf/tmp directories.

State and persistence: generated `tmp/`, `html/CIL_Reference_Guide.html`, and `pdf/CIL_Reference_Guide.pdf`.

Dependencies and integration points: called by `secilc/Makefile doc`; depends on pandoc, sed/gsed, Markdown guide files, policy test file, and `secil.xml`.

Risks and test signals: Markdown file list must stay synchronized with docs. Platform-specific sed choice is handled for Darwin. No validation beyond successful pandoc conversion.
