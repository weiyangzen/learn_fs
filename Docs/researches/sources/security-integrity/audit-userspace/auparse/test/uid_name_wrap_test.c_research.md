<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/uid_name_wrap_test.c -->
# sources/security-integrity/audit-userspace/auparse/test/uid_name_wrap_test.c

Purpose: regression test for name-to-uid and uid-to-name cache symmetry in auparse internal user lookup.

Important APIs and functions: calls internal `lookup_uid_from_name`, then uses `check_lru_uid` to inspect the uid cache and `destroy_lru` to release it.

Control flow and state: creates a zeroed stack `auparse_state_t`, resolves `"root"` to uid 0, verifies the cache node for uid 0 contains name `"root"`, and destroys the cache created during lookup. No external files are used, but the system user database must resolve root conventionally.

Dependencies and integration: includes private `internal.h`, `lru` structures through that header, and libc user lookup behavior.

Risks and test signals: catches cache population regressions and uid/name wraparound issues. Risk is platform sensitivity if uid 0 is not named root or NSS is unavailable. Success is exit zero.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/uid_name_wrap_test.c -->
