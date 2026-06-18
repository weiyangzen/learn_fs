# sources/user-network-fs/samba/source4/dsdb/samdb/samdb.h

## Purpose
`samdb.h` is the public DSDB/SAMDB interface header. It defines internal DSDB controls, extended-operation OIDs, replication flags, password-change control payloads, schema and partition constants, opaque names, and feature names used across Samba AD DC modules.

## Important APIs, Types, and Functions
Important definitions include `enum dsdb_password_checked`, `struct dsdb_control_current_partition`, `DSDB_REPL_FLAG_*`, password-change and password-validation controls, metadata/security-descriptor propagation controls, dbcheck controls, GMSA and KDC smartcard reset controls, `struct dsdb_extended_replicated_object`, `struct dsdb_extended_replicated_objects`, partition/rid/schema extended-operation structures, OpenLDAP dereference control structures, `struct samldb_msds_intid_persistant`, extended-DN and encrypted-connection opaques, Samba compatible feature names, and `SAMBA_LDB_WRAP_CONNECT_FLAG_NO_SHARE_CONTEXT`.

## Control Flow and Behavior
The header does not implement code, but it defines the control and extended-operation vocabulary that drives behavior across the LDB module stack. Many controls are module-to-module tokens rather than public LDAP controls, and their criticality/data payload contracts are enforced by individual modules.

## State and Persistence Behavior
Several structures describe persistent or replicated state: replicated object batches, linked attributes, partition DNs, schema metadata sequence names, password policy data, transaction GUIDs, and feature records. Opaque-name constants define in-memory LDB context state such as extended-DN storage format, partition module messages, full join replication completion, and encrypted connection status.

## Dependencies and Integration Points
It includes LDB, generated NDR security/SAMR/DRSUAPI/DRSBLOBS types, schema definitions, auth session structures, DSDB DN utilities, GMSA crypto, DSDB common prototypes, and common flag definitions. This is a high-fanout header used by SAMDB code, LDB modules, replication, KDC/password code, dbcheck, schema, and operational modules.

## Risks and Edge Cases
OID constants are compatibility contracts; changing or reusing them can break module interoperability and persisted controls. Several comments note special-case or internal-only semantics, such as bypassing password hashing, dbcheck repairs, RODC local lockout changes, and tombstone restore behavior. The misspelled `samldb_msds_intid_persistant` type is part of source compatibility. Header fanout means small include changes can produce broad rebuild or dependency cycles.

## Test Signals
Compile coverage across AD DC modules is essential. Behavioral test signals come from replication extended operations, password-change paths, dbcheck fix modes, schema update/load operations, security descriptor propagation, GMSA updates, OpenLDAP dereference handling, and feature negotiation for sorted links, encrypted secrets, and LMDB level one.
