# sources/security-integrity/selinux/libsemanage/src/iface_record.c

Purpose: wraps libsepol network-interface record APIs for libsemanage.

Important APIs/functions: compare/compare2/qsort, key create/extract/free, name get/set, interface context get/set, message context get/set, create/clone/free, and `SEMANAGE_IFACE_RTABLE`.

Control flow: operations are mostly direct calls to `sepol_iface_*`; the record table allows generic database code to clone, compare, key, and free interface records.

State/persistence: record allocation and owned strings/contexts are managed by libsepol. Persistence is through `interfaces_file.c` and `interfaces_policydb.c`.

Risks: qsort comparator is static because no local overlap validation uses it outside the record table. Callers must set both ifcon and msgcon before printing/persisting. Tests should cover name keying, context setters, clone/free, and parser behavior when one context is missing or invalid.
