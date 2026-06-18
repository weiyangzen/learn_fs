# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/admin.py

## Purpose
Defines `tahoe admin` subcommands for key generation, deriving public keys, migrating crawler state from pickle to JSON, and adding Grid Manager certificates to a storage server configuration.

## APIs, Types, And Control Flow
Option classes are `GenerateKeypairOptions`, `DerivePubkeyOptions`, `MigrateCrawlerOptions`, `AddGridManagerCertOptions`, and `AdminCommand`. `do_admin` dispatches via `subDispatch`. Key commands call Ed25519 helpers and print ASCII private/public strings. `migrate_crawler` upgrades `storage/lease_checker.state`, `storage/bucket_counter.state`, and `storage/lease_checker.history`. `add_grid_manager_cert` reads a cert from a file or stdin, parses it, loads node config, enables storage grid management, registers the cert in `[grid_manager_certificates]`, writes `<name>.cert`, and reports the count.

## State, Persistence, And Integration
Writes crawler JSON replacement files through storage crawler/expirer helpers. `add_grid_manager_cert` rewrites `tahoe.cfg` through `_Config.set_config` and writes certificate JSON in the node basedir. It integrates with `allmydata.client.read_config`, Grid Manager certificate parsing, `jsonbytes`, CLI basedir resolution, and Twisted `usage`.

## Risks And Test Signals
Risks include trusting local pickle inputs during migration, partial config/cert writes if the cert file write fails after config updates, and name collisions or invalid names becoming filenames. Key material is printed to stdout and must be handled securely by callers. Test signals include `allmydata/test/cli/test_admin.py`, grid manager tests, and crawler migration tests.
