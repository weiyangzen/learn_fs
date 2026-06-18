# sources/security-integrity/selinux/secilc/docs/secil.xml
# sources/security-integrity/selinux/secilc/docs/secil.xml

Purpose: Kate/Pandoc syntax definition for SELinux CIL (`*.cil`) highlighting.

Important APIs and control flow: XML `language` definition declares keyword lists for CIL block-start statements, functions, operators, and builtins; context rules detect parentheses, comments starting with `;`, strings, escaped chars, and nested blocks; item data maps token classes to style categories; general settings mark single-line comments and case-sensitive keywords.

State and persistence: static documentation asset used by pandoc during guide generation.

Dependencies and integration points: consumed by `secilc/docs/Makefile` via `--syntax-definition=secil.xml`.

Risks and test signals: keyword lists are manually derived from libsepol CIL sources and can become stale as language statements evolve. Broken XML would fail documentation builds.
