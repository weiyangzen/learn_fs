# sources/security-integrity/libcap/pam_cap/capability.conf

Purpose: sample `/etc/security/capability.conf` for `pam_cap.so`, documenting how PAM module arguments and capability rules are meant to be used.

Important format and behavior: each non-comment rule begins with an IAB/capability text token such as `all`, `none`, `!cap_chown`, `^cap_setuid`, or comma-separated IAB entries, followed by user selectors. Selectors can be exact users, `*`, or groups with `@group`. The first matching rule wins in `pam_cap.c`, so rule order is security relevant.

State, dependencies, integration: the file is consumed by `pam_cap.c` through `read_capabilities_for_user()`. It relies on libcap text parsing for the first field and NSS group/user lookup for matching.

Risks and test signals: the sample defaults to `none *`, preventing unspecified users from inheriting prior IAB state. Tests in `test_pam_cap.c` exercise this file's beta, gamma, alpha, and delta matching order and IAB effects.
