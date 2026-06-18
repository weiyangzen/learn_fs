# sources/user-network-fs/samba/source4/torture/drs/python/samba_tool_drs_critical.py

## Purpose
`samba_tool_drs_critical.py` is a focused blackbox regression test for `samba-tool drs clone-dc-database` when critical objects depend on a non-critical parent chain. It targets server behavior around `DRSUAPI_DRS_GET_ANC` combined with `DRSUAPI_DRS_CRITICAL_ONLY`.

## Important APIs, Types, And Functions
- `SambaToolDrsTests` extends `drs_base.DrsBaseTestCase`.
- The only test, `test_samba_tool_drs_clone_dc_critical_object_chain()`, uses live LDAP to move the Administrator object under a randomly named non-critical OU, then clones the DC database.
- Cleanup callbacks restore Administrator and delete the temporary OU.

## Control Flow
Setup collects `DC1`, `DC2`, and command credentials. The test connects to DC1 over LDAP, reads rootDSE, creates a random `OU=not-critical...` under the domain NC, renames the domain Administrator account (`SID-500`) into that OU, runs `samba-tool drs clone-dc-database`, opens the cloned local `sam.ldb`, and searches for `cn=administrator`. The final assertion requires the cloned Administrator DN to match the non-critical OU path.

## State And Persistence Behavior
The test temporarily moves the built-in Administrator object in the live domain, which is a significant directory mutation. `addCleanup()` restores Administrator to `CN=Users` and deletes the temporary OU. The clone is created in `self.tempdir` and cleanup removes generated Samba runtime directories.

## Dependencies And Integration Points
It depends on Samba LDAP helpers, SID binding rename syntax, `samba-tool drs clone-dc-database`, and local LDB inspection. The integration point is critical-object replication closure: a clone limited to critical objects must still replicate required ancestors so critical descendants have valid DNs.

## Risks
Moving Administrator is intrusive; cleanup correctness is essential. The test assumes the Administrator account has RID 500 and can be renamed in the test environment. Failures during clone could leave Administrator under the temporary OU until cleanup runs. It is sensitive to access control and protected-object behavior.

## Test Signals
The key signal is successful clone completion and exactly one Administrator object in the local clone, with DN equal to `cn=administrator,<temporary non-critical OU>`. Any clone failure or Administrator landing elsewhere indicates broken ancestor handling for critical-only replication.
