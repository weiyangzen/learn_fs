# Research: sources/user-network-fs/samba/source4/setup/tests/blackbox_group.sh

Purpose: blackbox coverage for `samba-tool group` and related user/contact membership commands against a freshly provisioned DC.

Control flow and APIs: it provisions `simple-dc`, creates users, verifies `user getgroups`, creates six groups across Domain/Global/Universal and Security/Distribution combinations, adds/removes users, tests primary group rules, creates contacts, tests `--object-types`, `--member-dn`, duplicate CN handling in OUs, `--member-base-dn`, group deletion, group listing, and listmembers. It uses subunit helpers `testit`, `testit_grep`, and expected-failure helpers.

State and persistence: it creates and deletes a target directory and mutates the provisioned `sam.ldb` through `samba-tool`.

Dependencies and risks: depends on `$PYTHON`, `$BINDIR/samba-tool`, NTVFS provisioning, and exact DN layout under `DC=foo,DC=example,DC=com`. Shell quoting limitations are noted in comments. Strong signals are expected failure matching for invalid primary group and ambiguous object lookups.
