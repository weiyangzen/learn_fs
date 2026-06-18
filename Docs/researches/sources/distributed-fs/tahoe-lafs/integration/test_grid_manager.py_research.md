# sources/distributed-fs/tahoe-lafs/integration/test_grid_manager.py

## Purpose
Exercises the Grid Manager CLI and Grid Manager certificate enforcement in live Tahoe grids. It verifies key creation, certificate signing, client add/remove behavior, public identity reporting, and storage-server acceptance/rejection based on signed certificates.

## Important APIs, Types, and Functions
`_run_gm` runs `allmydata.cli.grid_manager` in a subprocess, optionally under coverage, and raises `util.ProcessFailed` with combined output on non-zero exit. The tests use `ed25519.signing_keypair_from_string`, `ed25519.string_from_verifying_key`, `base32.a2b`, and `configutil.get_config`. The grid scenarios use `create_grid`, storage node `restart`, `grid.add_client`, and `util.run_tahoe admin add-grid-manager-cert`.

## Control Flow
Certificate tests create a Grid Manager config on stdin, add named storage-server public keys, sign certificates, then verify signatures with the Grid Manager public key. File-backed config tests create a config directory and inspect `config.json` after add/remove operations. Rejection setup builds a two-server grid but gives only one server a valid certificate, configures client `diana` with happy=2 and the Grid Manager public key, and expects upload failure with `UploadUnhappinessError`. Acceptance setup signs both servers, restarts them, configures client `freya`, and expects upload success. Identity test compares the CLI-reported public key to the key derived from stored private config.

## State and Persistence
Grid Manager state is either streamed through stdin/stdout JSON or persisted in a temp config directory as `config.json`. Storage servers persist certs in their node directories and require restart for cert changes. Client trust roots are persisted in `tahoe.cfg` under `[grid_managers]`.

## Dependencies and Integration Points
Integrates Grid Manager CLI, Tahoe admin CLI, Ed25519 certificate primitives, storage node key files (`node.pubkey`), Tahoe config writing, and live grid/client lifecycle from `integration.grid` and `integration.util`.

## Risks
The enforcement tests are helper-named with leading underscores and may rely on external collection or manual enabling. They are expensive because they create and restart multiple nodes. The failure assertion accepts only `UploadUnhappinessError`; unrelated process failures are re-raised as generic assertion failures with limited diagnosis.

## Test Signals
Signals include valid Ed25519 signatures, expected JSON storage-server membership, exact public-key byte equality, upload rejection when one certified server cannot satisfy happiness, and upload success when all required servers have certificates.
