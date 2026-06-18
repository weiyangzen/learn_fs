## sources/security-integrity/audit-userspace/audisp/audispd-llist.h

Purpose: list data structures and helpers for dispatcher plugin configs.

It defines `lnode` wrapping `plugin_conf_t *`, `conf_llist` with head/current/count, inline `plist_first`, `plist_count`, and `plist_get_cur`, plus list operations. State is external to callers. Dependencies are `audispd-pconfig.h` and compiler attribute macros. Risks are exposed mutable list internals and single-cursor design unsuitable for nested iteration. Test signals are pconfig/list unit tests in the audit dispatcher test directory.
