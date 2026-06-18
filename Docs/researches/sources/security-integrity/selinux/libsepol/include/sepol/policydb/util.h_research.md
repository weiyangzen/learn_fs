# sources/security-integrity/selinux/libsepol/include/sepol/policydb/util.h

Purpose: Declares miscellaneous internal utility helpers for arrays, AV formatting, extended permissions formatting, and tokenization.

Important APIs and functions: `add_i_to_a`, `sepol_av_to_string`, `sepol_extended_perms_to_string`, and `tokenize`.

Control flow: Formatting helpers convert permission bitmasks to textual names for diagnostics/conversion; `tokenize` parses delimited strings as an `sscanf` replacement.

State and persistence: `add_i_to_a` grows caller-owned arrays. Formatting functions allocate strings that callers must free.

Dependencies and integration points: Used by assertion reporting, conversion code, and parsers.

Risks: Formatting failures affect diagnostics for security violations. Caller ownership of returned strings/arrays must be clear.

Test signals: AV/xperm formatting for known/unknown bits, allocation failure paths, and tokenization edge cases validate it.
