# File Research: sources/virtualization/spdk/app/spdk_nvme_discover/discovery_aer.c

## Purpose
Connects to an NVMe-oF discovery controller, prints the discovery log page, registers for discovery asynchronous event notifications, and reprints the log when discovery changes occur.

## Main Entry Points
- `parse_args()` handles transport ID, debug/log flags, and host NQN.
- `set_trid()` initializes and parses the NVMe transport ID, defaulting to the discovery NQN.
- `get_discovery_log_page()` submits a discovery log retrieval.
- `get_log_page_completion()` prints the discovery log and handles pending re-fetch requests.
- `aer_cb()` validates discovery AER completions and triggers another log fetch.
- `setup_sig_handlers()` installs SIGINT/SIGTERM handlers.
- `main()` initializes env, connects to the discovery controller, registers the AER callback, performs initial fetch, processes admin completions until shutdown, detaches, and finalizes.

## Internal Mechanics
The program tracks `g_discovery_in_progress` and `g_pending_discovery` so overlapping AER-triggered log requests are coalesced. The main loop only processes admin completions; all discovery log and AER activity completes through admin completion callbacks.

`print_discovery_log()` decodes generation counter, record count, record format, transport type, address family, subsystem type, port/controller IDs, service ID, subsystem NQN, and transport address.

## Dependencies
Uses SPDK env, NVMe, NVMe-oF discovery log structures, transport ID parsing, endian helpers, logging, signal handling, and admin completion processing.

## Filesystem/Block Relevance
Discovery records identify remote NVMe subsystems and endpoints that can later be used as block devices by SPDK NVMe-oF clients.

## Risks and Notes
- The transport ID is mandatory and must target an NVMe-oF discovery subsystem, not PCIe.
- Errors in AER or discovery-log commands terminate the process.
- Keep-alive/transport failure is represented by the main exit flag comment, but shutdown is primarily signal-driven in this file.
