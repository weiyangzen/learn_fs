# sources/security-integrity/selinux/libsemanage/src/database_policydb.h

Purpose: declares the generic policydb adapter API and object-specific policydb method table shape.

Important APIs/types/functions: defines `record_policydb_table_t` callbacks for add, modify, set, query, count, exists, and iterate over `sepol_policydb_t`; declares `dbase_policydb_init`, `attach`, `detach`, `release`, and `SEMANAGE_POLICYDB_DTABLE`.

Control flow: object-specific policydb code supplies callback tables; the generic backend handles caching, attachment, and common database semantics.

State and persistence behavior: backend state can be path-backed or attached to a shared in-memory policydb. Persistence to disk is indirect through direct API policy writes.

Dependencies and integration points: includes libsepol handle/policydb headers plus semanage database and handle internals. Used by booleans and other policy-backed record families.

Risks: callbacks must be consistent with generic record comparison and clone semantics. Test signals include policydb adapter initialization for each record family and attach/detach during direct commit.
