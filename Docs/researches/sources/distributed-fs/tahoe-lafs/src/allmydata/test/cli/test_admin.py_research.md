# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_admin.py

## Purpose
Tests selected `tahoe admin` CLI behaviors: migration of crawler state away from pickle and adding Grid Manager certificates to a node directory.

## Important APIs, Types, And Functions
`AdminMigrateCrawler` checks `migrate-crawler` output and usage text. `fake_cert` is a minimal signed Grid Manager certificate fixture. `AddCertificateOptions` tests option parsing and certificate input validation. `AddCertificateCommand` tests the actual `add_grid_manager_cert()` operation, including first-add success and duplicate-name failure.

## Control Flow
Tests build temporary storage or node directories with Twisted `FilePath`, parse command-line arguments through top-level `Options`, descend through nested `subOptions`, inject `StringIO` streams, and call admin functions directly. Certificate tests load JSON from stdin or a file, then assert parsed `certificate_data`, created files, return codes, and stderr messages.

## State And Persistence
The tests create temporary storage directories, `lease_checker.state.json`, minimal `tahoe.cfg`, and certificate files such as `zero.cert`. They do not touch global config outside test temp paths.

## Dependencies And Integration Points
Depends on `allmydata.scripts.admin`, runner `Options`, Tahoe JSON-bytes utilities, Twisted `UsageError` and `FilePath`, and `SyncTestCase`.

## Risks And Test Signals
Important risks are silent acceptance of malformed certificate JSON, unclear stdin read failures, duplicate certificate overwrite, and regressions in migration messaging. Signals include usage text mentioning pickle security, "Already converted" detection, `UsageError` for empty or incomplete cert data, successful cert file creation, certificate count messages, and duplicate-name return code 1.
