# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/dhclient.c

## Purpose
Main FreeBSD DHCP client implementation. It parses options, initializes privilege separation and Capsicum, discovers the target interface, drives the DHCP state machine, validates leases/options, persists lease state, monitors route/interface events, and delegates privileged operations to a helper process.

## Main Elements
- Process setup:
  - `main()` initializes Casper syslog, parses `-bcdlnpqu`, creates pid/lease paths, reads config, checks link, starts `PREINIT`, discovers the interface, forks the privileged child, reads/rewrites leases, enters Capsicum/chroot fallback, drops to `_dhcp`/`nobody`, starts the state machine, and dispatches events.
  - `init_casper()` opens `system.syslog`.
  - `go_daemon()` daemonizes once, rewrites pidfile, closes/nulls descriptors, and limits Capsicum rights.
- Route/interface monitoring:
  - `findproto()` and `get_ifa()` parse routing socket address lists.
  - `routehandler()` reacts to address deletion, interface down/departure, link changes, and 802.11 association changes.
  - `disassoc()` expires active lease state after wireless roam/disassociation.
- DHCP state machine:
  - `state_reboot()`, `state_init()`, `state_selecting()`, `state_bound()`, and `state_panic()` implement INIT-REBOOT, DISCOVER/OFFER selection, renewal, and fallback to recorded leases.
  - `send_discover()`, `send_request()`, and `send_decline()` send DHCP packets with randomized exponential backoff and lease timeout handling.
  - `dhcpoffer()`, `dhcpack()`, `dhcpnak()`, `bootp()`, and `dhcp()` validate transaction IDs/hardware addresses, reject configured servers, and dispatch packet types.
- Packet and lease construction:
  - `make_discover()`, `make_request()`, and `make_decline()` assemble BOOTP/DHCP packets and options.
  - `packet_to_lease()` copies packet options, ignores configured options, validates selected option classes, records address/server/file fields, and handles unsafe characters.
  - `bind_lease()` writes the lease, optionally changes MTU through privsep, runs the script, replaces active lease, schedules renewal, and daemonizes.
- Lease persistence:
  - `rewrite_client_leases()` rewrites the lease database with descriptor rights limits.
  - `write_client_lease()` emits dhclient lease syntax, options via `pretty_print_option()`, and GMT renew/rebind/expire times.
  - `free_client_lease()` releases option/server/file allocations.
- Script and privsep messaging:
  - `script_init()`, `script_write_params()`, and `script_go()` send imsg-style buffers to the privileged child.
  - `priv_script_init()`, `priv_script_write_params()`, and `priv_script_go()` build the script environment and execute the script.
  - `fork_privchld()` runs the privileged event loop and calls `dispatch_imsg()`.
- Validation helpers:
  - `check_option()` validates IP-list options, hostname/domain/search options, classless routes, and unknown-option policy.
  - `check_classless_option()` enforces RFC 3442 width/length rules and masks route destinations.
  - `res_hnok()`, `check_search()`, `ipv4addrs()`, and `option_as_string()` validate/export string forms.

## Dependencies And Integration
Central coordinator for `dhcpd.h` structures, `dispatch.c` event loop, `bpf.c` packet I/O, `options.c` option parsing/assembly, `clparse.c` configuration and lease parsing, `privsep.c` privileged messages, `dhclient-script`, Casper syslog, Capsicum, route sockets, pidfiles, and interface ioctls.

## Risk Notes
This file is security-sensitive: it consumes network-provided options, builds shell-script environments, and crosses a privilege boundary. It includes explicit validation for hostnames, domain search lists, classless routes, MTU minimums, command substitution characters, and unsafe boot fields. State transitions and timeout arithmetic are also subtle, especially around expiry/renew/rebind overflow and route socket changes.
