# sources/security-integrity/selinux/libsemanage/src/node_record.c

Purpose: wraps libsepol network node record APIs for libsemanage.

Important APIs/functions: compare/compare2/qsort, key create/extract/free, address and mask get/set in string and byte forms, protocol get/set/string, context get/set, create/clone/free, and `SEMANAGE_NODE_RTABLE`.

Control flow: methods delegate to `sepol_node_*`, passing the semanage handle's sepol handle where required. Protocol string mapping is delegated to libsepol. The record table is consumed by generic file and policydb databases.

State/persistence: node objects are allocated/freed by libsepol wrappers. Persistence is through `nodes_file.c` and `nodes_policydb.c`.

Risks: address/mask setters require matching protocol semantics; parse code must set protocol before address/mask. Tests should cover IPv4 and IPv6 addresses/masks, byte getters, key extraction, clone/free, and sorting behavior used by merge operations.
