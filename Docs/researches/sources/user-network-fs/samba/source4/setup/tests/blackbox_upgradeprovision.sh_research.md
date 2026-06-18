# Research: sources/user-network-fs/samba/source4/setup/tests/blackbox_upgradeprovision.sh

Purpose: blackbox regression test for `samba_upgradeprovision`.

Control flow: it provisions reference, normal-upgrade, and full-upgrade DC databases from the same 2008_R2 base schema. It runs `samba_upgradeprovision --debugchange` and `--full --debugchange`, then compares upgraded databases to the reference with `samba-tool ldapcmp`, both normal and security-descriptor modes, skipping missing DNs and filtering `servicePrincipalName`.

State and dependencies: creates three provision directories and removes them. Depends on `samba-tool`, `samba_upgradeprovision`, and database comparison semantics.

Risks and test signals: the test checks a null-upgrade scenario, so it is strongest for idempotency and template drift, not for real old production databases. LDAP compare results are strong structural signals.
