# sources/security-integrity/audit-userspace/rules/43-module-load.rules

Purpose: audits kernel module insertion and removal through syscalls rather than program watches.

Important rules: b32/b64 `init_module,finit_module` key `module-load`; b32/b64 `delete_module` key `module-unload`.

Control flow: syscall exit filters.

State and persistence: kernel audit rules.

Dependencies and integration: requires architecture syscall mappings.

Risks and test signals: may miss module activity performed before audit rules are loaded. Test with controlled module load/unload and search the module keys.
