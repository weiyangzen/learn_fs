<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/common/common.h -->
# sources/security-integrity/audit-userspace/common/common.h

Purpose: internal common header for audit userspace utilities, visibility, atomic wrappers, constants, and message APIs.

Important APIs and types: defines `AUDIT_ATOMIC_STORE/LOAD`, `FORMAT_BUF_LEN`, fallback `strndupa`, hidden declarations for string splitting, event-ending classification, runlevel helpers, program name lookup, time conversion constants/functions, console/wall messaging, `message_t`, `debug_message_t`, and `_set_aumessage_mode`.

Control flow and state: header-only macros choose C11 atomics when configured, otherwise direct volatile-compatible access. Visibility macros hide internal symbols from public ABI.

Dependencies and integration: includes `config.h`, `dso.h`, `gcc-attributes.h`, and system limits/types. Used across common, auplugin, and daemon code.

Risks and test signals: atomics use relaxed ordering, sufficient only for simple flags if callers do not require stronger synchronization. Macro fallback and hidden visibility must stay compatible with all consumers. Build coverage across components is the main signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/common/common.h -->
