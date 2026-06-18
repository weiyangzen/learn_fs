## sources/security-integrity/audit-userspace/audisp/audispd-llist.c

Purpose: simple linked list for plugin configurations.

It initializes lists, appends copied `plugin_conf_t` records, iterates with current pointer, counts active plugins, clears memory, marks entries unchecked, and finds unchecked/name matches for reload reconciliation. State is heap nodes and shallow-copied plugin configs; `free_pconfig` must later release fields inside copied configs. Dependencies are allocation, string compare, and `audispd-pconfig.h`. Risks include shallow struct copy ownership assumptions, append requiring `cur` to point at the tail for nonempty lists, no internal locking, and current-pointer iteration invalidation during mutation. Tests should cover reload matching, duplicate names, and clear/free behavior.
