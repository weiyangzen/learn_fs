<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/release-4-5-0-pre1/add-deleted-user.sh -->
# sources/user-network-fs/samba/source4/selftest/provisions/release-4-5-0-pre1/add-deleted-user.sh

Purpose: fixture-generation helper that creates and deletes a user to capture deleted-object and deactivated-link state.

Important APIs/types/functions: `SAMBA_TOOL`, `samba-tool user/group add`, `group addmembers`, `user delete`, and `ldbsearch --show-recycled --show-deleted --show-deactivated-link --reveal`.

Control flow: targets `st/provision/simple-dc/private/sam.ldb`, creates user `fred`, creates group `swimmers`, adds membership, deletes `fred`, and greps revealed deleted/recycled output for `fred` and `swimmers`.

State and persistence behavior: mutates the simple-dc test provision and is intended to help create/update an LDB dump fixture.

Dependencies and integration points: tied to `make test TESTS="samba4.blackbox.group.py"` and simple-dc provision paths.

Risks: hardcoded DB and destination paths. It does not write the dump itself despite defining `DEST`.

Test signals: grep output showing deleted user and group link state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/release-4-5-0-pre1/add-deleted-user.sh -->
