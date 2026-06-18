# sources/user-network-fs/samba/source3/script/tests/test_winbind_ignore_domains.sh

Purpose: integration test for `winbind:ignore domains`, verifying that authentication from a trusted domain succeeds normally and is blocked after the trusted domain is ignored.

Important functions and APIs: uses `ldbsearch`, `ldbmodify`, `smbcontrol winbindd reload-config`, `wbinfo -p`, and smbclient helpers from `common_test_fns.inc`. `add_posix_ids()` and `remove_posix_ids()` modify `uidNumber`/`gidNumber` attributes for trusted-domain Administrator, Domain Users, and Domain Admins.

Control flow: derive the trusted domain base DN, add POSIX IDs, clear injected config, reload winbind, verify trusted-domain NTLM by IP, NTLM by FQDN, and Kerberos by FQDN all work. Then write `winbind:ignore domains = TRUST_DOMAIN`, reload winbind, verify the same three accesses fail, clear config again, reload, and remove the POSIX IDs.

State and persistence: mutates trusted-domain LDAP attributes and local `global_inject.conf`. Cleanup is explicit at the end but not protected by a trap.

Dependencies and integration: registered as `samba3.blackbox.winbind_ignore_domain` in `ad_member_idmap_ad:local`. It requires a trusted domain fixture, idmap AD semantics, Kerberos and NTLM test credentials, and working winbind reload behavior.

Risks and test signals: failures before `remove_posix_ids()` can leave LDAP attributes behind. Passing signal is the before/after contrast: three successful accesses without the ignore setting and three expected failures with it.
