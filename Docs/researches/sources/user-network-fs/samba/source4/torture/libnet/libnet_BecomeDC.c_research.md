# sources/user-network-fs/samba/source4/torture/libnet/libnet_BecomeDC.c

## Purpose

`libnet_BecomeDC.c` tests the libnet BecomeDC workflow. It joins a machine account as a workstation, runs the vampire replication callbacks to build a local private database, marks the replicated RootDSE synchronized, commits, reopens the SAM database with system credentials, verifies schema loading, and then optionally un-becomes/unjoins.

## Important APIs, Types, and Functions

- `torture_net_become_dc()` is the test entry point.
- `torture_temp_dir()` creates an isolated target directory.
- `torture_join_domain()` creates a temporary workstation trust account and returns `struct test_join`.
- `libnet_vampire_cb_state_init()` prepares callback state and local database paths.
- `libnet_BecomeDC()` performs the replication workflow using callbacks `check_options`, `prepare_db`, `schema_chunk`, `config_chunk`, and `domain_chunk`.
- `libnet_vampire_cb_ldb()` and `libnet_vampire_cb_lp_ctx()` expose the replicated LDB and loadparm context.
- `samdb_connect()`, `dsdb_uses_global_schema()`, and `dsdb_get_schema()` verify the resulting database.
- `libnet_UnbecomeDC()` and `torture_leave_domain()` perform cleanup unless disabled by a torture option.

## Control Flow

The test creates a temp directory, chooses a destination DC NetBIOS name from `become dc:smbtorture dc` or defaults to `smbtorturedc`, resolves the source DC host, and joins the domain as a workstation trust account. It initializes vampire callback state with the joined domain names and output location, creates a libnet context using command-line credentials, fills `libnet_BecomeDC` input domain/source/destination fields, and runs BecomeDC.

After successful replication, it modifies `@ROOTDSE` to set `isSynchronized=TRUE`, commits the LDB transaction, detaches and reopens `sam.ldb` from the generated private directory as system, asserts the reopened DB does not use the global schema, and fetches a loaded `dsdb_schema`. Cleanup calls `libnet_UnbecomeDC()`, leaves the domain, and frees callback state unless `become dc:do not unjoin` is set.

## State and Persistence Behavior

This is a stateful integration test. It creates a temporary machine account in the domain, writes replicated database and secrets under a temp private directory, modifies local `@ROOTDSE`, commits an LDB transaction, and normally unjoins/removes the machine account. If `do not unjoin` is enabled or a failure interrupts cleanup, domain and filesystem artifacts may remain.

## Dependencies and Integration Points

It integrates libnet join, BecomeDC/UnbecomeDC, DRSUAPI/DRS blob structures, vampire callbacks, SAMDB/DSDB schema loading, auth system session, loadparm private-dir override, name resolution, and torture RPC/join helpers. It is registered as `net.api.become.dc`.

## Risks and Edge Cases

The test has a large blast radius: network resolution, domain join rights, replication permissions, local private directory setup, transaction commit, schema load, and cleanup all must work. Cleanup assertions run even after failures, so missing context from early setup can complicate failure handling. The `do not unjoin` option intentionally leaves state behind for debugging.

## Test Signals

Strong success signals are successful name resolution, workstation join, `libnet_BecomeDC()`, RootDSE modification, transaction commit, reopened `sam.ldb`, `dsdb_uses_global_schema()` returning false, non-null `dsdb_schema`, successful `libnet_UnbecomeDC()`, and successful domain leave.
