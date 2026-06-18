# sources/security-integrity/audit-userspace/lib/private.h

Purpose: internal libaudit header for hidden APIs, remote auditd message-wrapper protocol constants, endian packing helpers, and shared parser state declarations.

Important APIs/types: defines `hide_t`, `struct auditd_remote_message_wrapper`, `AUDIT_RMW_*` protocol constants, pack/unpack macros, `audit_send`, `__audit_send`, `audit_msg`, `audit_send_user_message`, internal permission lookup prototypes, `_audit_parse_syscall`, and parser globals such as `_audit_permadded`, `_audit_archadded`, `_audit_syscalladded`, `_audit_exeadded`, `_audit_filterfsadded`, and `_audit_elf`.

Control flow: macro-based serialization writes and reads little-endian protocol fields in byte buffers. Function declarations connect libaudit internals and hide selected symbols with `AUDIT_HIDDEN_START/END`.

State and persistence: declares process-global parser flags and current ELF architecture used across audit rule parsing. The remote wrapper protocol carries sequence ids but this header has no storage.

Dependencies and integration: depends on `stdint.h`, `dso.h`, and `libaudit` structures. Used by netlink, lookup, auditctl, auditd remote logging paths, and parser code.

Risks and test signals: macros evaluate arguments directly and assume an `unsigned char *` buffer with enough length. Protocol constants must remain stable for remote auditd compatibility. Parser globals require careful reset between rule lines; `auditctl.c::reset_vars` is the main control signal.
