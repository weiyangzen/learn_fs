# sources/user-network-fs/samba/source4/dsdb/tests/python/confidential_attr.py

Purpose: this security regression suite verifies that confidential, RODC-filtered, and ACL-denied attributes cannot be disclosed by LDAP search filters, returned attributes, DirSync, deleted-object searches, or timing differences.

Important APIs/types/functions: `ConfidentialAttrCommon` builds the shared OU/users, modifies schema `searchFlags`, opens sealed admin and user `SamDB` connections, and defines assertion helpers for exact-match, wildcard, inverse, and negative searches. `ConfidentialAttrTest` covers confidential attributes and allow/neutral ACEs. `ConfidentialAttrTestDenyAcl` covers object and object-attribute deny ACEs. `ConfidentialAttrTestDirsync` adapts assertions to `dirsync:1:1:1000`, deleted objects, preserve-on-delete, and timing-attack checks. `RodcFilteredAttrDirsync` adds `GUID_DRS_GET_CHANGES` and uses `dirsync:1:0:1000` to test RODC-filtered attributes.

Control flow: setup creates an OU, one secret-bearing user, one unprivileged user, and additional users with the tested attribute. Tests first prove normal visibility, then set `SEARCH_FLAG_CONFIDENTIAL` or other flags, apply DACLs through `SDUtils`, and repeat searches as user and admin. DirSync tests search from the naming context base and add filters to restrict results to the fixture. The timing test creates `msFVE-RecoveryInformation`, crafts slow matching-rule filters, and compares timing uncertainty ranges.

State and persistence behavior: this suite mutates schema `searchFlags`, user objects, DACLs, deleted objects, and default confidential data. Cleanup restores searchFlags where registered and tree-deletes the OU. Failed runs can leave schema flags or DACL changes, so the setup includes a defensive reset for the selected attribute flags.

Dependencies and integration points: depends on Samba DSDB constants, LDB modify/search APIs, `sd_utils`, sealed GENSEC connections, NT security descriptors, DirSync controls, deleted-object filtering, and Windows-compatible confidential attribute semantics.

Risks: schema mutation is global and high impact. Timing assertions may be noisy on slow or loaded systems. Some negative-search expected behavior is documented as Windows-like hiding and varies by access rights. The host parsing branch uses `host.lstrip(start + 3)`, which is not a correct way to remove a URL prefix and is fragile if later code relies on bare `host`.

Test signals: result counts for filter families, attribute presence/absence checks for `None`, `*`, and specific attrs, admin sanity checks, expected no-results behavior for hidden DirSync attrs, deleted-object non-disclosure, and overlapping user timing ranges all signal correct protection.
