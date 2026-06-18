<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_downgrade_db -->
# sources/user-network-fs/samba/source4/scripting/bin/samba_downgrade_db

Purpose: downgrades a Samba AD database from newer LDB storage/index formats to formats older Samba releases can read.

Important APIs/types/functions: command option `-H/--URL`; raw `ldb.Ldb` with `modules:` disabled; `SamDB`; `dbcheck.reindex_database`; `ldb.PACKING_FORMAT` and `PACKING_FORMAT_V2`; `@PARTITION` and `@INDEXLIST` metadata.

Control flow: the script opens `sam.ldb` or the supplied URL without creating it, reads `@PARTITION`, and branches on `backendStore`. LMDB (`mdb`) is reopened with `pack_format_override` and committed to rewrite pack-format metadata. TDB-style stores disable `dsdb:guid index`, replace `@IDXGUID` and `@IDX_DN_GUID` on the main DB and partition databases, then reopen through the full Samba stack and trigger reindexing.

State and persistence behavior: directly modifies database metadata and partition indexes in transactions. It does not create backups. A later Samba 4.8+ or 4.11+ tool can re-upgrade the database automatically, as noted by the script output.

Dependencies and integration points: depends on Samba loadparm, LDB internals, partition layout under the private directory, and `dbchecker`. It is an administrative migration utility for offline or carefully controlled AD DB compatibility work.

Risks: destructive format changes occur in-place. Missing backups, unexpected partition paths, or running services can leave a difficult recovery situation. LMDB handling only downgrades pack format because GUID index removal is not safe with long DNs.

Test signals: successful transaction commits, printed downgrade messages, and a subsequent `dbcheck` reindex are the main signals. Compatibility should be validated by opening the DB with the target older Samba version.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_downgrade_db -->
