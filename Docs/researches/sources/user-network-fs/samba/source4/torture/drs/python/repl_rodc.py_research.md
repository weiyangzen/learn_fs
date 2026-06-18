# sources/user-network-fs/samba/source4/torture/drs/python/repl_rodc.py

## Purpose
`repl_rodc.py` is a Samba DRS torture test module for replication involving a read-only domain controller (RODC), with emphasis on secret replication, password-replication policy, and `msDS-RevealedUsers` metadata. It creates a temporary RODC account and joins enough RODC objects to exercise `DsGetNCChanges` as both administrator and RODC machine credentials.

## Important APIs, Types, And Functions
- `drs_get_rodc_partial_attribute_set()` builds a `drsuapi.DsPartialAttributeSet` by walking `attributeSchema`, excluding constructed, non-replicated, and RODC-filtered attributes, converting names through a temporary RODC schema.
- `DrsRodcTestCase` extends `drs_base.DrsBaseTestCase` and relies on `_ds_bind()`, `_getnc_req10()`, `_exop_req8()`, LDAP handles, and common DRS helpers from that base.
- `_create_rodc()` configures `DCJoinContext` fields for an RODC join, including never-reveal and reveal SIDs, `UF_PARTIAL_SECRETS_ACCOUNT`, RODC secure channel type, and DRS special secret processing flags.
- `_assert_in_revealed_users()` decodes `msDS-RevealedUsers` binary DN values using `BinaryDn` and `ndr_unpack(drsblobs.replPropertyMetaData1)` to check expected secret ATTIDs.

## Control Flow
`setUp()` creates a test OU, constructs a randomized RODC identity, creates RODC directory objects through `DCJoinContext`, opens a temporary samdb for schema ATTID conversion, builds RODC machine credentials, and binds DRS twice: once as admin and once as the RODC. Each test then creates users, sets passwords, optionally changes password-replication group membership, builds a `DsGetNCChanges` request for `DRSUAPI_EXOP_REPL_SECRET`, and asserts either success or `ERROR_DS_DRA_SECRETS_DENIED` (`8630`). The suite also tests follow-on requests that attempt to switch from a permitted chunked request to a secret request.

## State And Persistence Behavior
The test mutates live directory state: it creates a test OU, users, password values, RODC computer objects, local allow/deny attributes (`msDS-RevealOnDemandGroup`, `msDS-NeverRevealGroup`), and `msDS-RevealedUsers`. Cleanup delegates RODC object removal to `cleanup_old_join()` and base cleanup. State validation focuses on metadata versions and USNs in revealed-user entries, including password changes that should update `replPropertyMetaData1`.

## Dependencies And Integration Points
This file integrates Python bindings for `drsuapi`, `drsblobs`, `security`, `misc`, `ldb`, `Credentials`, `DCJoinContext`, Samba test helpers, and Samba DRS base helpers. It exercises server-side DRS secret handling, RODC PRP logic, ATTID mapping, binary DN metadata, and the join code path used to materialize RODC directory objects.

## Risks
The tests are timing-sensitive around metadata update visibility and include a five-second sleep noted as still flaky against Windows. They depend on exact ATTID lists and sorted PAS behavior. Several tests use broad exception handling, which can mask unexpected failures. The RODC setup mutates sensitive directory structures and must always clean up correctly to avoid later test contamination.

## Test Signals
Strong signals include denial with error `8630`, successful admin override, RODC success only when allowed by PRP, PAS ignored for secret replication, mismatch denial when one RODC tries to use another RODC's destination DSA, and `msDS-RevealedUsers` entries containing the five expected password-secret ATTIDs with correct version/USN changes.
