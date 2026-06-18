# sources/distributed-fs/tahoe-lafs/integration/util.py

## Purpose
Shared integration-test infrastructure for spawning Tahoe processes, collecting output, managing node lifecycle, waiting for readiness/filesystem events, performing HTTP/CLI operations, generating SSH/RSA keys, representing upload formats, and reconfiguring nodes.

## Important APIs, Types, and Functions
Process helpers include `block_with_timeout`, `dump_python_output`, `dump_output`, `_ProcessExitedProtocol`, `ProcessFailed`, `_CollectOutputProtocol`, `_DumpOutputProtocol`, and `_MagicTextProtocol`. Tahoe lifecycle APIs include `run_tahoe`, `_tahoe_runner_optional_coverage`, `TahoeProcess`, `_run_node`, `basic_node_configuration`, and `_create_node`. Blocking helpers include `run_in_thread`, `await_file_contents`, `await_files_exist`, `await_file_vanishes`, `cli`, `node_url`, `web_get`, `web_post`, and `await_client_ready`. Crypto/format helpers include `generate_ssh_key`, `CHK`, `SSK`, `upload`, `reconfigure`, and `generate_rsa_key`.

## Control Flow
Subprocesses are spawned through Twisted reactors, with output either collected into memory, dumped to stdout, or watched for a magic readiness string. `_create_node` invokes `create-node`, applies common config, then starts the node. `_run_node` starts `tahoe run` with Eliot logging and registers cleanup finalizers. `await_client_ready` polls the web JSON status until enough recently active servers are visible. `reconfigure` compares desired shares/convergence/segment-size settings against current config, writes only changed values, restarts if needed, and waits for readiness.

## State and Persistence
Writes Tahoe node directories, `tahoe.cfg`, private convergence config, Eliot logs, generated SSH keys, temporary RSA key files for mutable upload, and uploaded Tahoe shares/capabilities. It also registers pytest finalizers that terminate live node processes.

## Dependencies and Integration Points
Core dependencies are Twisted process/deferred APIs, pytest-twisted, requests, Paramiko, cryptography RSA serialization, Tahoe config utilities, Tahoe client config reader, and `allmydata.scripts.runner`. This file is the central integration point used by most tests in the directory.

## Risks
Several helpers mix blocking and asynchronous code; using them outside `run_in_thread`/Deferred contexts can stall the reactor or fill process output buffers. `_MagicTextProtocol` readiness depends on log text. `await_client_ready` assumes status JSON shape and wall-clock liveness. `upload` is typed as accepting `TahoeProcess` but current test usage passes a grid client with `.process`, so callers must match the actual wrapper shape. Cleanup blocks on process exit and can hang until timeout if a process ignores termination.

## Test Signals
This is support code rather than a test file; its signals are reliable process failure propagation, captured stdout/stderr, readiness polling success, exact file appearance/content waits, HTTP 2xx enforcement, and deterministic key/format argument generation for higher-level tests.
