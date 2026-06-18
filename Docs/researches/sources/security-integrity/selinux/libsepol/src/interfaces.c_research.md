# sources/security-integrity/selinux/libsepol/src/interfaces.c

Purpose: adapts high-level network interface records to policydb `OCON_NETIF` object-context entries. It supports existence, query, modify, count, and iteration operations.

Important APIs and functions: public APIs are `sepol_iface_exists`, `sepol_iface_query`, `sepol_iface_modify`, `sepol_iface_count`, and `sepol_iface_iterate`. Internal converters are `iface_from_record` and `iface_to_record`.

Control flow: `iface_from_record` allocates an `ocontext_t`, duplicates the interface name, converts interface and message contexts into `context[0]` and `context[1]`, and returns the node. Query/existence scan `OCON_NETIF` by name. Modify converts the new record, replaces an existing same-name node if found, or prepends the node otherwise. Iterate converts each node to a temporary high-level record and invokes a callback.

State and persistence behavior: mutates the in-memory `policydb->ocontexts[OCON_NETIF]` linked list. Unlike pkey/endport modify, interface modify replaces existing keys and frees the old name and contexts. Serialization is handled elsewhere.

Dependencies and integration points: depends on context conversion, handle/debug, public interface APIs, policydb object contexts, `expand.c` object-context copying, and kernel-to-CIL `netifcon` output.

Risks: replacement frees only the old node fields expected for `OCON_NETIF`, so the list must contain valid interface contexts. All operations are linear scans. Error cleanup must destroy both contexts if conversion partially succeeds.

Test signals: modify insert and replace paths, query after replacement, count stability, two-context conversion round trips, callback early-stop/failure, empty list behavior, and allocation/context-conversion failure cleanup.
