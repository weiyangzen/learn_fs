# sources/security-integrity/libcap/pam_cap/pam_cap.c

Purpose: PAM module that assigns inheritable, ambient, and bounding capability policy to users using libcap IAB text.

Important APIs/types/functions: `struct pam_cap_s` stores parsed module arguments. `load_groups()` gathers primary and supplemental group names. `read_capabilities_for_user()` scans the capability config and returns the first matching capability text. `set_capabilities()` parses and applies `cap_iab_t`, handling `all`, `none`, fallback defaults, `keepcaps`, and deferred application. PAM entry points are `pam_sm_authenticate()` and `pam_sm_setcred()`.

Control flow: authentication reads rules only to decide PAM success versus ignore unless `autoauth` is set. Credential establishment rereads the config, builds an IAB tuple, and either calls `cap_iab_set_proc()` immediately or stores it with `pam_set_data()` for `iab_apply()` during `pam_end()`.

State and dependencies: uses NSS, PAM, syslog, libcap, `prctl(PR_SET_KEEPCAPS)`, and config file metadata. It zeroes config/group strings before free.

Risks and test signals: first-match rule order, redundant auth/setcred reads, NSS failures, deferred cleanup semantics, and config permissions are key risks. It rejects world-writable config files except `/dev/null`. `test_pam_cap.c` covers parser flags, group matching, no-user `PAM_INCOMPLETE`, fallback, and capability vector changes.
