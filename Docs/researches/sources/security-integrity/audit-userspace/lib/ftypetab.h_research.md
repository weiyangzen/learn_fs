# sources/security-integrity/audit-userspace/lib/ftypetab.h

Purpose: Lookup input mapping POSIX file type mode bits to audit file type names.

Important entries: `socket`, `link`, `file`, `block`, `dir`, `character`, and `fifo` mapped from `S_IF*` constants.

Control flow: No runtime logic; generated into `ftypetabs.h`.

State and persistence: Static mapping compiled into libaudit.

Dependencies and integration: Used by `audit_name_to_ftype`, `audit_ftype_to_name`, and `AUDIT_FILETYPE` rule parsing.

Risks: Names are user-facing rule syntax. Constants must come from appropriate system stat headers through generator includes.

Test signals: Parse and reverse lookup all file types; validate `filetype` is accepted only for exit filters.
