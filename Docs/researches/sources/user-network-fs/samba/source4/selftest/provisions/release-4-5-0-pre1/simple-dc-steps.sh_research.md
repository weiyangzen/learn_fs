<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/release-4-5-0-pre1/simple-dc-steps.sh -->
# sources/user-network-fs/samba/source4/selftest/provisions/release-4-5-0-pre1/simple-dc-steps.sh

Purpose: documented shell steps for reproducing simple-DC group/deleted-user fixture state.

Important APIs/types/functions: `make test TESTS=samba4.blackbox.group.py`, `samba-tool user add`, `group add`, `group addmembers`, `user delete`, and `ldbsearch` with deleted/recycled/deactivated-link controls.

Control flow: runs the group blackbox test to prepare a provision, adds user and group, shows state before deletion, deletes the user, and shows state after deletion.

State and persistence behavior: mutates `st/provision/simple-dc/private/sam.ldb`.

Dependencies and integration points: selftest fixture authoring helper for release-4-5-0-pre1 provision data.

Risks: hardcoded paths and credentials/password. Intended for manual fixture generation, not general automation.

Test signals: before/after `ldbsearch` output for `fred` and `swimmers`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/release-4-5-0-pre1/simple-dc-steps.sh -->
