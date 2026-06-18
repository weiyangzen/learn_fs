# sources/security-integrity/selinux/libsemanage/src/booleans_policydb.c

Purpose: adapts libsepol policydb boolean helpers into the semanage generic policydb database framework.

Important APIs/types/functions: defines `SEMANAGE_BOOL_POLICYDB_RTABLE` with sepol boolean add/modify/set/query/count/exists/iterate function pointers, plus `bool_policydb_dbase_init` and `bool_policydb_dbase_release`.

Control flow: init calls `dbase_policydb_init` with the generic boolean record table and policydb extension table; release delegates to `dbase_policydb_release`.

State and persistence behavior: the resulting backend reads or mutates an attached or cached `sepol_policydb_t`. In direct commit, local boolean changes are merged into this policydb before the kernel policy is written.

Dependencies and integration points: depends on libsepol `bools.h`, `SEMANAGE_BOOL_RTABLE`, and `database_policydb`. It is the policy-side counterpart to the local file and active backends.

Risks: function-pointer table correctness is critical because generic wrappers assume uniform semantics. Test signals are policydb add/modify/query/list behavior and successful merge of local boolean overrides during commit.
