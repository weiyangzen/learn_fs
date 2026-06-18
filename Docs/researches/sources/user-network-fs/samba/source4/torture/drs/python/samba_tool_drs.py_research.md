# sources/user-network-fs/samba/source4/torture/drs/python/samba_tool_drs.py

## Purpose
`samba_tool_drs.py` is a blackbox test suite for the `samba-tool drs` command family. It validates bind, KCC, options, replicate variants, local replication semantics, machine credentials, and `clone-dc-database` behavior with and without secrets.

## Important APIs, Types, And Functions
- `SambaToolDrsTests` extends `drs_base.DrsBaseTestCase`.
- `_get_rootDSE()` opens LDAP or local LDB SamDB connections and returns rootDSE attributes.
- `runsubcmd()`, `check_output()`, `_run_drs_kcc()`, `_net_drs_replicate()`, and inbound replication toggles come from the base/test framework.
- Local helper `get_num_obj_links()` parses object/link counts from `samba-tool drs replicate --local` output.

## Control Flow
Setup reads `DC1` and `DC2` environment variables and builds explicit command-line credentials. Basic tests run individual `samba-tool drs` subcommands and assert success text. Replicate tests cover synchronous/asynchronous DRS replication, `--local-online`, `--local`, full versus incremental counts, and `-P` or implicit machine credentials. The local replication test creates a temporary joined DC, performs full and incremental local pulls, creates a linked group/user change, verifies that pulling from the source sends objects plus one link, then verifies pulling from a peer with an up-to-dateness vector sends zero. Clone tests build a local clone, inspect rootDSE identity, verify secrets are excluded unless `--include-secrets`, and test demoting another DC out of the cloned database.

## State And Persistence Behavior
The file creates temporary join databases under `self.tempdir`, local `etc/private/state` directories, groups, users, and cloned `sam.ldb` databases. It disables inbound replication in one local replication scenario and restores it in teardown. TearDown also removes common Samba runtime files and directories from the working directory.

## Dependencies And Integration Points
This module integrates Samba command-line tools, live LDAP, local LDB databases, domain join/demote, replication metadata, up-to-dateness vectors, linked attribute replication, and secret-filtering behavior. It acts as end-to-end coverage from CLI parsing through DRS internals and database mutation.

## Risks
Assertions on command output text can break on wording changes even when behavior remains correct. Parsing object/link counts by scanning integers is brittle. Temporary joins must use unique NetBIOS names to avoid collisions. Clone/demote tests mutate local databases heavily and depend on exact object layout for server, NTDS Settings, machine, and optional DNS account objects.

## Test Signals
Signals include expected output fragments (`Site GUID`, `Repl epoch`, `successful`, `was started`, `Current DSA options`), full replication returning more objects than incremental replication, linked local replication returning at least two objects and one link, second pull returning zero objects/links, cloned rootDSE matching source server identity, `krbtgt` password absent unless secrets are included, successful removal of the other DC from a clone, and clone without `--targetdir` failing.
