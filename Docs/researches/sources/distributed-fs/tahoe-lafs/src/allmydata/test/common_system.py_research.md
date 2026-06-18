<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_system.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_system.py

Purpose: Provides integration-test infrastructure for running actual introducer and client nodes in-process, with deterministic certificates, assigned ports, HTTP cleanup, and connection polling.

Important APIs and functions: `SYSTEM_TEST_CERTS` supplies precomputed Tub cert/key PEMs. `flush_but_dont_ignore`, `_render_config`, `_render_config_section`, and `_render_section_values` support teardown and config generation. `spin_until_cleanup_done` waits for reactor file descriptors and delayed calls to drain. `SystemTestMixin` owns node grid setup, HTTP client pool tuning, service parenting, introducer/client config generation, node bouncing, extra-node creation, and connection readiness checks.

Control flow: `setUp` enables optional blocking detection, activates HTTP storage client test mode, installs a `SameProcessStreamEndpointAssigner`, and starts a `MultiService`. `_create_introducer` writes introducer config and optional fixed certs, then starts an introducer. `set_up_nodes` creates the introducer, writes client configs, starts the first client to capture helper fURL, starts remaining clients, waits for introducer/storage connectivity, and records web URLs. `tearDown` stops services, flushes Foolscap events, closes HTTP pools, and spins for reactor cleanup.

State and persistence: Writes `tahoe.cfg`, `private/introducers.yaml`, `private/node.pem`, and helper fURL files under each test basedir. Keeps process-local service parent, client list, introducer URL, helper fURL, web URLs, and HTTP connection pools. Certificate material is static test-only data.

Dependencies and integration points: Uses Twisted reactor/services, Foolscap flushing, Tahoe client/introducer creation, file utilities, storage client classes, HTTP client factory test hooks, `pollmixin`, `StallMixin`, and `SameProcessStreamEndpointAssigner`.

Risks: Fixed certificates are expired and suitable only for controlled tests. `spin_until_cleanup_done` reaches into reactor internals such as `_internalReaders`. Connection waiting can take up to 200 seconds and assumes every client should connect to every storage server. Aggressive HTTP timeouts are tuned for local tests and may be brittle on loaded hosts.

Test signals: Validate both Foolscap and HTTP storage modes, helper fURL propagation, client bounce and extra-node behavior, service shutdown without dirty reactors, port assignment reuse, HTTP pool closure, and correct server-class assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_system.py -->
