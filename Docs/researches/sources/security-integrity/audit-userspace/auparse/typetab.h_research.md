<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/typetab.h -->
# sources/security-integrity/audit-userspace/auparse/typetab.h

Purpose: macro table mapping audit field names to `auparse_type_t` interpretation categories.

Important APIs and types: entries use `_S(AUPARSE_TYPE_*, "field")` for uid/gid, syscall, arch, exit, escaped strings, escaped file paths, keys, permissions, modes, socket addresses, capabilities, success, syscall arguments, signal, session, capability bitmaps, netfilter protocol, ICMP type, protocol/address, AppArmor fields under `WITH_APPARMOR`, seccomp, open/mmap flags, MAC labels, proctitle, hooks, fanotify, trust, and errno.

Control flow and state: no code executes here; the include site defines `_S` to generate lookup records. Conditional AppArmor rows depend on build configuration.

Dependencies and integration: consumed by auparse field-type lookup and interpretation paths, including Python binding `get_field_type` exposure. Any field added here changes how raw audit values are interpreted and searched.

Risks and test signals: incorrect classification can alter user-visible interpretations or break golden tests. Coverage comes from parser references, lookup tests for generated functions, and tests that call `interpret_field`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/typetab.h -->
