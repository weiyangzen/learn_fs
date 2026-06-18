<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/common/strsplit.c -->
# sources/security-integrity/audit-userspace/common/strsplit.c

Purpose: lightweight space-delimited tokenizer variants for audit userspace.

Important APIs and functions: `audit_strsplit_r` is reentrant and similar to `strtok_r` but splits only on literal space characters, skips leading spaces, writes NUL terminators into the source string, and updates caller save pointer. `audit_strsplit` stores static state and delegates to the reentrant version.

Control flow and state: the reentrant function is caller-state driven; the non-reentrant wrapper uses a static `char *str`. `#pragma GCC optimize("O3")` requests optimized code for this tokenizer.

Dependencies and integration: declared in `common.h` and compiled into `libaucommon.la`. Used by parsers/config readers that want shell-light splitting rather than full whitespace tokenization.

Risks and test signals: it does not split tabs or other whitespace, mutates input, and the non-reentrant wrapper is not thread-safe. Tests are indirect unless dedicated tokenizer tests exist elsewhere.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/common/strsplit.c -->
