<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_upgradeprovision -->
# sources/user-network-fs/samba/source4/scripting/bin/samba_upgradeprovision

Purpose: legacy Samba AD provision upgrader that compares the current provision against a freshly generated reference provision, backs up state, and updates databases, schema-related objects, secrets, passwords, DNS support files, GPO metadata, and security descriptors.

Important APIs/types/functions: global copy filters `attrNotCopied`, overwrite policy `hashOverwrittenAtt`, link/backlink tracking, `check_for_DNS`, `populate_links`, `populateNotReplicated`, `populate_dnsyntax`, `sanitychecks`, `handle_special_case`, `add_missing_object`, `add_missing_entries`, `handle_links`, `checkKeepAttributeWithMetadata`, `update_present`, `reload_full_schema`, `update_partition`, `rebuild_sd`, `backup_provision`, `sync_calculated_attributes`, and helpers imported from `samba.upgradehelpers`.

Control flow: after parsing debug/full/backup/very-old flags, the script gets current paths and LDB handles, creates a backup under the private directory, starts grouped transactions, derives provision names and previous provision USN ranges, sanity-checks for a single DC, creates a reference provision in a temp directory, opens its LDBs, loads schema/link metadata, updates base samdb metadata, prepares a schema reload closure, optionally performs full partition update, updates secrets and machine/DNS account passwords, recalculates security descriptors when needed, updates OEM/provision USN/GPO/policy IDs, commits both DB sets, reopens samdb to trigger reindexing, and deletes the reference provision. Exceptions leave the backup and exit nonzero.

State and persistence behavior: creates a full database/sysvol backup, a temporary reference provision, and many transactional DB changes. It can copy TDB/LMDB partition files, move old partition files into `sam.ldb.d`, modify samdb objects and descriptors, update secrets.ldb, change account passwords, create DNS config templates, update GPOs, and write provision USN ranges.

Dependencies and integration points: deeply integrated with Samba provisioning internals, schema loading, LDB transactions, NDR security descriptors, DRS replication metadata, xattr-preserving sysvol copies, TDB/MDB copy utilities, DNS provisioning files, and GPO update helpers.

Risks: this is high-impact operational migration code with many version-specific special cases. Incorrect USN range detection can overwrite administrator changes or skip needed updates. The single-DC sanity check prevents unsupported multi-DC upgrades. Rollback relies on the backup directory rather than automatic restore. Some legacy branches are only useful for very old alpha provisions.

Test signals: successful grouped commits, "Upgrade finished", backup presence on failure, reindex reopen success, and debug categories for object changes and security descriptors. Strong tests require fixture provisions from multiple historical releases and validation that schema, secrets, DNS, GPO, and SD state match expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_upgradeprovision -->
