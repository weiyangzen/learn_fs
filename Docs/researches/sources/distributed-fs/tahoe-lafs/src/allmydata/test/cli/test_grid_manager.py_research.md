# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_grid_manager.py

## Purpose
This module tests the Grid Manager CLI and the `tahoe admin add-grid-manager-cert` subcommand. It validates grid-manager config creation, stdout config mode, public identity, server add/list/remove/sign flows, error handling, file permissions, and certificate installation into a node directory.

## Important APIs, Types, and Functions
- `GridManagerCommandLine.setUp` creates a `click.testing.CliRunner`.
- `invoke_and_check` runs a Click command and re-raises exceptions with their traceback, then asserts exit code zero.
- `GridManagerCommandLine` covers `grid_manager --config ... create`, `public-identity`, `list`, `add`, `sign`, and `remove`.
- `TahoeAddGridManagerCert` uses `run_cli("admin", "add-grid-manager-cert", ...)` to test the Tahoe admin subcommand.

## Control Flow
Click tests run inside isolated filesystems and inspect resulting files such as `config.json` and `storage0.cert.N`. Some tests feed config JSON through stdin with `--config -` and inspect stdout. Add/sign flows create a manager, add a storage server public key, sign certificates, parse JSON output, and confirm certificate content. Admin tests run the Tahoe CLI with missing arguments or stdin cert data, then inspect `tahoe.cfg` and written cert files.

## State and Persistence Behavior
Grid Manager state persists under the configured directory as `config.json` plus certificate files named by storage server and sequence. The admin command persists a certificate file such as `foo.cert` and updates `tahoe.cfg` with a `[grid_managers]` style mapping. Permission tests temporarily chmod the config directory to make certificate creation fail, skipping on Windows and superuser runs where permission semantics differ.

## Dependencies and Integration Points
This module depends on `allmydata.cli.grid_manager.grid_manager`, Click's test runner, Tahoe `jsonbytes`, Twisted Trial, `FilePath`, platform detection, and `run_cli`. It bridges the standalone Click-based grid-manager CLI with the Twisted/Tahoe admin command surface.

## Risks and Edge Cases
Risks include invalid config JSON producing friendly errors, accidental overwrite on repeated create, duplicate storage server names, missing servers for remove/sign, certificate sequence numbering, stdin/stdout config handling, platform-specific permission behavior, and missing required admin options.

## Test Signals
The suite has strong CLI-level signals: real command invocation, file layout checks, JSON parsing, and error-output assertions. It does not validate cryptographic certificate verification deeply; it mainly confirms command mechanics and persistence format.
