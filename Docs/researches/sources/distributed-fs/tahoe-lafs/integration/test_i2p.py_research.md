# sources/distributed-fs/tahoe-lafs/integration/test_i2p.py

## Purpose
Defines integration support for I2P transport testing: local i2pd startup, I2P introducer creation, anonymous node creation, and a skipped end-to-end storage exchange over I2P.

## Important APIs, Types, and Functions
`i2p_network` starts `purplei2p/i2pd:release-2.45.1` via Docker and waits for `_MagicTextProtocol("ephemeral keys")`. `i2p_introducer` creates and runs an introducer with `--listen=i2p`, rewrites config via `read_config`, and waits for "introducer running". `i2p_introducer_furl` polls for `private/introducer.furl`. `_create_anonymous_node` creates a hidden-IP I2P node and writes a minimal config. `test_i2p_service_storage` is skipped.

## Control Flow
Module-level skips disable all tests when Docker is unavailable or on Windows. The network fixture launches i2pd with a bad reseed URL so it remains local. The introducer fixture creates an introducer directory if absent, configures web/logging settings, runs it, and terminates it on finalization. The skipped test creates two anonymous nodes, uploads a file through one CLI process, extracts the capability from stdout, downloads through the other, and compares bytes.

## State and Persistence
Temporary introducer and node directories contain Tahoe config, introducer furl, web port, and log gatherer settings. Docker runs as an external process and is cleaned up by INT. Node configs enable `[i2p]`.

## Dependencies and Integration Points
Requires Docker, a specific i2pd image, Tahoe runner, Twisted process management, `write_introducer`, `read_config`, `FilePath`, and allocated web ports.

## Risks
The only end-to-end test is explicitly skipped because I2P tests are nonfunctional. Fixed Docker host port `7656` can conflict with local services. Polling for furl creation has no explicit timeout. Cleanup depends on process signaling and Twisted deferred completion.

## Test Signals
Current live signal is fixture startup readiness. If unskipped, the intended signal is successful capability transfer: upload through Carol and byte-identical retrieval through Dave over I2P.
