# sources/distributed-fs/tahoe-lafs/integration/test_tor.py

## Purpose
End-to-end integration for Tor transport: onion-service storage nodes and anonymous client access to a normal grid.

## Important APIs, Types, and Functions
`test_onion_service_storage` creates two anonymous Tor nodes and exchanges data between them. `upload_to_one_download_from_the_other` is an async helper that shells out to Tahoe `put` and `get`, comparing downloaded bytes. `_create_anonymous_node` creates a node with `--hide-ip`, `--listen tor`, Tor control port, and share parameters, then writes Tor onion config before starting the node.

## Control Flow
Windows is skipped at module level; `test_anonymous_client` is skipped on macOS. Onion-service storage creates Carol and Dave with total shares 2, waits up to 600 seconds for both to see two servers, uploads through Carol, downloads through Dave. The anonymous-client test creates a normal storage node, then an anonymized Tor client with total shares 1, waits up to 1200 seconds, and downloads data uploaded through the normal node.

## State and Persistence
Each anonymous node gets a temp node directory with introducer data, web port, base Tahoe config, and `[tor]` settings including onion private key path. Uploads create real Tahoe capabilities and shares in the fixture grid.

## Dependencies and Integration Points
Requires the `tor_network` fixture and its `client_control_endpoint`, Tahoe runner, introducer fixtures, `write_introducer`, `basic_node_configuration`, client readiness polling, and Twisted process protocols.

## Risks
Transport tests are slow and platform-sensitive. The helper includes a TODO questioning whether Tor usage is actually proven. Long readiness timeouts increase CI duration. Hard-coded web/onion external ports can conflict in parallel runs.

## Test Signals
Signals are readiness with required server counts and byte-identical transfer across nodes when one or both nodes are configured to use Tor.
