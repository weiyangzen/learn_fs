# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/samba_dsdb.c

## Purpose
`samba_dsdb.c` implements the bootstrap LDB module that constructs Samba's full DSDB module chain at runtime. It lets provisioned databases keep a stable top-level module while Samba changes internal module ordering and feature handling. The file also registers `dsdb_flags_ignore`, a helper module that strips internal DSDB metadata flags before passing add/modify messages down.

## Important APIs, Types, And Functions
`read_at_rootdse_record()` reads `@ROOTDSE` for naming context attributes needed to configure partition module routing. `prepare_modules_line()` builds `modules` attribute values of the form `backendDN:module1,module2,...` for the partition module's opaque configuration message. `check_required_features()` validates that `@SAMBA_DSDB` required features are known to this Samba version. `samba_dsdb_init()` is the central initializer: it registers Samba LDB handlers, checks DSDB feature records, builds the ordered module list, prepares partition-module configuration, loads the module list in reverse for LDB, installs it as the next chain, and initializes the chain under a read lock.

`dsdb_flags_ignore_fixup()` shallow-copies add/modify messages and removes `DSDB_FLAG_INTERNAL_FORCE_META_DATA` from element flags; if an element only carried that flag and has no values, it removes the element. `dsdb_flags_ignore_add()` and `dsdb_flags_ignore_modify()` rebuild requests with the fixed message. `ldb_samba_dsdb_module_init()` registers both `samba_dsdb` and `dsdb_flags_ignore`.

## Control Flow
Initialization first registers DSDB syntax/handler support and constructs DNs for `@SAMBA_DSDB`, `@INDEXLIST`, and the partition control record. If `@SAMBA_DSDB` exists, required features are checked against the features this code understands. Old compatible features are pruned depending on whether `@INDEXLIST` says Samba feature options are supported; modifications are wrapped in direct lower-module transactions.

The final DSDB module list is assembled in semantic order: `resolve_oids`, `rootdse`, notification/schema/load/lazy commit and query-control modules, `extended_dn_store`, `extended_dn_in`, audit/objectclass/security/password/samldb/instancetype modules, TDB/link modules such as `repl_meta_data`, `encrypted_secrets`, `operational`, `linked_attributes`, `extended_dn_out_ldb`, and final notification/partition modules. Because LDB loads lists in reverse, the code reverses the final list before `ldb_module_load_list()`.

Partition configuration is built from `@ROOTDSE`: one line routes the schema naming context through `schema_data` plus backend modules, and one wildcard line routes other backends through the backend module list. The resulting message is stored in the `DSDB_OPAQUE_PARTITION_MODULE_MSG_OPAQUE_NAME` opaque, also used by gMSA code as proof of local DB access.

## State And Persistence
The module stores the constructed partition configuration as an LDB opaque and rewires the in-memory module chain. It may persistently modify `@SAMBA_DSDB` compatible-feature values during startup cleanup. Otherwise state is process-local and derived from database control records. `dsdb_flags_ignore` has no durable state; it only normalizes request flags.

## Dependencies And Integration Points
This file is the integration point for nearly the whole DSDB LDB stack. It depends on LDB module loading, DSDB module helpers, Samba feature constants, `@ROOTDSE`, `@SAMBA_DSDB`, `@INDEXLIST`, partition module opaques, encrypted secrets feature flags, LMDB feature flags, and Samba handler registration. Ordering is critical because downstream modules assume prior modules have expanded object classes, resolved DNs, enforced ACLs, generated metadata, or routed partitions.

## Risks And Test Signals
Module ordering is the main risk: moving entries can break security, schema loading, linked attributes, or partition routing. Feature-gate handling is another risk, especially refusing databases with unknown required features and pruning compatible features without losing data needed by older/newer versions. `indexlist_dn` has a defensive check typo that tests `samba_dsdb_dn` after allocating `indexlist_dn`; allocation-failure tests would catch this pattern. Tests should cover bootstrap on empty and existing databases, unknown required features, compatible-feature cleanup with and without `@INDEXLIST`, exact module order, partition opaque contents, read-lock cleanup on init failure, and `dsdb_flags_ignore` add/modify behavior for empty and non-empty forced-metadata elements.
