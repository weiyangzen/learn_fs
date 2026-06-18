<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/test_samba3dump.sh -->
# sources/user-network-fs/samba/source4/selftest/test_samba3dump.sh

Purpose: blackbox selftest wrapper verifying that `samba3dump` completes on bundled Samba3 test data.

Important APIs/types/functions: `testprogs/blackbox/subunit.sh`, `subunit_start_test`, `subunit_pass_test`, `subunit_fail_test`, `$PYTHON`, and `source4/scripting/bin/samba3dump`.

Control flow: starts a subunit test named `samba3dump`, computes source root, runs `samba3dump` against `testdata/samba3`, and reports pass/fail through subunit helpers.

State and persistence behavior: no expected persistent writes beyond tool behavior/output.

Dependencies and integration points: part of Samba selftest blackbox scripts and validates the Samba3 dump conversion script.

Risks: only checks command success, not dump content correctness.

Test signals: subunit pass or fail for `samba3dump`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/test_samba3dump.sh -->
