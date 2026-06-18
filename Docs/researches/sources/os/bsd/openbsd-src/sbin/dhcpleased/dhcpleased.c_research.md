# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/dhcpleased.c

## Purpose
`dhcpleased.c` is the privileged main process for the DHCP client daemon. It starts the engine and frontend children, brokers file descriptors, applies interface and route configuration, writes lease files, and handles reload/shutdown orchestration.

## Main Responsibilities
- Parses command-line flags for debug, child mode, config path, no-action config check, socket path, and verbosity.
- Parses configuration in full builds and supports `-n` validation/printing.
- Enforces root execution, singleton lockfile, and `_dhcp` user availability.
- Forks/execs engine and frontend child processes with an inherited imsg fd at descriptor 3.
- Creates main-to-child and frontend-to-engine socketpairs, including fd-passing setup.
- Opens privileged route, ioctl, BPF, control, and UDP resources and passes descriptors to children.
- Sets up route-socket filters for frontend interface/proposal events.
- Applies `unveil` restrictions for config, `/dev/bpf`, and lease storage.
- Dispatches imsgs from frontend and engine.
- Configures and deconfigures IPv4 addresses via `SIOCAIFADDR` and `SIOCDIFADDR`.
- Installs and withdraws routes by writing `RTM_ADD`/`RTM_DELETE` messages with label `dhcpleased`.
- Proposes or withdraws DNS resolver state with `RTM_PROPOSAL`.
- Writes lease files atomically under `/var/db/dhcpleased/`.
- Reads existing lease files so the engine can attempt INIT-REBOOT behavior.
- Manages config reload and config transfer to frontend/engine.

## Important Control Flow
- `main()` starts as coordinator unless invoked with `-E` or `-F`, in which case it enters the engine or frontend process function.
- `main_imsg_send_ipc_sockets()` creates the direct frontend-engine imsg channel and passes one end to each child.
- `main_dispatch_frontend()` handles BPF open requests, reload/log verbosity control, and interface updates from the frontend.
- `main_dispatch_engine()` applies engine requests for interface config/deconfig, route withdrawal, and DNS proposal/withdrawal.
- `configure_interface()` adds the leased address, routes, creates a bound UDP socket for renewal unicasts, passes it to the frontend, and writes the lease file.
- `deconfigure_interface()` removes the leased address; route deletion is intentionally disabled in one code block because removing the address lets the kernel clean interface routes without breaking duplicate-gateway cases.
- `configure_routes()` classifies direct, default, and gateway routes and may install a host route to an off-subnet default gateway.
- `main_reload()` parses a new config, sends it to children, then replaces the main copy.

## Dependencies and Integration
This file ties together `bpf`, `frontend`, `engine`, `control`, route sockets, ioctl interface configuration, lease file persistence, and config parsing. It is the only process retaining the privileges needed to mutate network state and open BPF.

## Risk Notes
The main process treats invalid imsg payload shapes as fatal, which is appropriate for trusted child-process protocol integrity. Lease file support is disabled if `unveil(_PATH_LEASE)` fails. Route message construction manually pads sockaddr payloads, so correctness depends on matching kernel routing socket ABI expectations.
