# sources/security-integrity/audit-userspace/rules/71-networking.rules

Purpose: simple network connection visibility rule.

Important rule: b64 `accept,connect` exit rule with key `external-access`.

Control flow: single syscall filter.

State and persistence: kernel audit rule state.

Dependencies and integration: x86_64/b64-focused as shipped; no b32 equivalent.

Risks and test signals: very broad network activity logging and incomplete cross-arch coverage. Test with outbound connect or inbound accept and search key `external-access`.
