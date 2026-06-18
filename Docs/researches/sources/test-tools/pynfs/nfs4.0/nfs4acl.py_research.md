<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/nfs4acl.py -->
# sources/test-tools/pynfs/nfs4.0/nfs4acl.py

Purpose: utility module for translating between POSIX-like mode bits and NFSv4 ACL ACE lists, validating ACLs that map to POSIX semantics, and printing ACLs.

Important APIs/types/functions: constants define file and directory read/write/execute masks, owner/all flag sets, default inheritance flags, used bits, ACE types, and mode lookup tables. `mode2acl()` creates six ACEs for OWNER@, GROUP@, and EVERYONE@ allow/deny pairs. `acl2mode()` derives octal mode from first matching allow/deny ACEs. `maps_to_posix()` validates ACL shape and delegates to `chk_owners()`, `chk_groups()`, and `chk_everyone()`. `chk_pair()` and `chk_triple()` enforce complementary allow/deny masks and repeated mask structure. `printableacl()` formats ACEs.

Control flow/state: functions are pure transformations/validators over ACE lists except that validators delete elements from a working copy. No persistent state exists.

Dependencies/integration: imports generated NFSv4 constants and `nfsace4` type. Tests use it to generate expected ACLs and verify server-returned ACL mapping.

Risks/test signals: `acl2mode()` contains a likely typo `perm[keys] = 0`, which would raise if a named ACE is missing. Mapping comments acknowledge incomplete checks for legal access-mask sets and flag combinations. Failures surface as `ACLError` or mismatched mode/ACL expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/nfs4acl.py -->
