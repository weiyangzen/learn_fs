<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/get-descriptors -->
# sources/user-network-fs/samba/source4/scripting/bin/get-descriptors

## Purpose

`get-descriptors` compares security descriptors between a local Samba AD database and a remote LDAP server, optionally producing LDIF modifications to align local descriptors with remote ones.

## Important APIs, Types, and Functions

`DescrGetter` owns local/remote LDB connections, domain DNs/SIDs, and descriptor maps. Methods include `get_domain_local_sid()`, `get_domain_remote_sid()`, `read_descr_by_base()`, `read_desc()`, `write_desc_to_ldif()`, `add_to_ldif()`, and `write_as_sddl()`.

## Control Flow

The script requires local domain, remote domain, and remote host. It opens local `SamDB` and remote LDAP, reads local and remote domain SIDs, searches schema/configuration/domain subtrees for `nTSecurityDescriptor`, maps descriptors by relative DN, compares SDDL after translating remote descriptors to the local SID, and prints either SDDL or LDIF replacement entries.

## State and Persistence Behavior

It is read-only against both directories and writes comparison output to stdout. The generated LDIF, if applied separately, would mutate local descriptors.

## Dependencies and Integration Points

It depends on Samba Python bindings, LDB paged search modules, NDR packing/unpacking, security descriptor/SID conversion, and credentials.

## Risks and Edge Cases

There is a typo in the description comment, and `add_to_ldif()` uses Python division in a range expression that may be invalid under Python 3 if long lines occur. `write_desc_to_ldif()` can reference `descr` before assignment if SDDL strings match but `opts.as_ldif` handling still reaches output. It requires high remote privileges.

## Test Signals

Tests should compare known local/remote fixture descriptors, exercise `--as-ldif` line folding, no-difference entries, SID translation, missing descriptor attributes, and remote bind failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/get-descriptors -->
