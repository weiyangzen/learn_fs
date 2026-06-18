# sources/user-network-fs/samba/source4/torture/drs/python/ridalloc_exop.py

## Purpose
`ridalloc_exop.py` tests RID allocation through `DsGetNCChanges` extended operation `DRSUAPI_EXOP_FSMO_RID_ALLOC`, plus offline RID master seizure and RID Set repair behavior. It also contains two replication-link tests for locally deleted objects in joined databases.

## Important APIs, Types, And Functions
- `DrsReplicaSyncTestCase` extends `drs_base.DrsBaseTestCase`.
- `_determine_fSMORoleOwner()` discovers RID FSMO owner/non-owner metadata, server account DNs, and RID Set DNs.
- `_check_exop_failed()` validates level-6 EXOP failure replies.
- `_test_join()` and `_test_force_demote()` create and remove temporary DC joins.
- Tests use `SamDB`, `dbcheck`, `drs_utils.drs_Replicate`, `system_session`, `admin_session`, `ndr_pack(security.dom_sid(...))`, and command wrappers for `fsmo seize`, `domain join`, and `domain demote`.

## Control Flow
The first tests build level-8 EXOP requests using base `_exop_req8()`, bind to the FSMO owner, and validate either unknown-caller failure for an invalid destination DSA or a successful three-object response containing RID Manager, target RID Set, and target server account. Role-transfer tests modify `becomeRidMaster`, allocate from the new master, and restore the original role in `finally`. Offline tests join a temporary DC, open its local `sam.ldb`, manipulate `fSMORoleOwner`, inspect or repair `rIDSetReferences`, and verify RID Set creation through `fsmo seize`, `dbcheck`, or `newuser()`. Later tests inject out-of-range object SIDs and verify `dbcheck` advances `rIDNextRid` and handles range rollover after seizure.

## State And Persistence Behavior
The test creates temporary joined DC directories under `self.tempdir`, modifies offline databases, seizes roles inside those local DBs, creates users/groups, and force-demotes corresponding server accounts from the live domain. It also temporarily transfers the live RID Master and restores it. Temporary directories are removed with `shutil.rmtree()`.

## Dependencies And Integration Points
Integration points include DRSUAPI EXOP replies, RID Manager FSMO state, Samba domain join/demote tooling, offline SamDB mutation, `dbcheck` RID Set repair, SID allocation, and replication metadata when linked attributes reference locally deleted objects. The final tests set `DSDB_FULL_JOIN_REPLICATION_COMPLETED_OPAQUE_NAME` to distinguish transaction-time full-join replication behavior.

## Risks
This is a high-risk test module because it changes FSMO role ownership, creates temporary DCs, seizes RID roles, and manipulates RID pools. Cleanup through demotion and role restoration must run even on assertion failure. Some checks assume exact object counts in DRS EXOP replies, except linked attribute counts are relaxed because RODCs can add links to server account objects. Duplicate user names in the rollover test may be environment-sensitive.

## Test Signals
Signals include level-6 EXOP responses, `DRSUAPI_EXOP_ERR_UNKNOWN_CALLER` for invalid DSA, `DRSUAPI_EXOP_ERR_SUCCESS` with three expected objects for valid RID allocation, `rIDSetReferences` appearing after seizure/dbcheck/user creation, `dbcheck` reporting fixed RID Set errors, `rIDNextRid` moving to injected high SID values, RID pool rollover after seizure, transaction commit failure before setting the full-join opaque, and success after setting it.
