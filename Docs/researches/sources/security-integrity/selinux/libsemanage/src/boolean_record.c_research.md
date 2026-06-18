# sources/security-integrity/selinux/libsemanage/src/boolean_record.c

Purpose: implements `semanage_bool_t` and `semanage_bool_key_t` as thin wrappers around libsepol boolean records while adding semanage-specific name substitution for alternate policy roots.

Important APIs/types/functions: exports key create/extract/free, comparisons, name/value getters and setters, create/clone/free, qsort comparator, and the `SEMANAGE_BOOL_RTABLE` generic record table.

Control flow: most functions delegate directly to `sepol_bool_*`. `semanage_bool_set_name` temporarily adjusts the libselinux policy root to the semanage selected store, applies `selinux_boolean_sub`, restores the original root, and stores the substituted name in the sepol record.

State and persistence behavior: record objects are heap-backed libsepol values. Persistent effects occur only when records are later written through file, policydb, or active backends. The temporary policy-root switch is process-global and must be restored carefully.

Dependencies and integration points: depends on libsepol boolean records, libselinux policy-root/boolean substitution APIs, semanage root/store config, and the generic database method table.

Risks: policy-root switching is sensitive to errors and thread safety. `semanage_bool_set_name` requires a valid SELinux policy root and can fail before allocating a substituted name. Test signals include name substitution under alternate roots, clone/free ownership, qsort ordering, and no leaked or stuck policy root on failures.
