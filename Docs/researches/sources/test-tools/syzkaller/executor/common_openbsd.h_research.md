<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_openbsd.h -->
# sources/test-tools/syzkaller/executor/common_openbsd.h

## Purpose

`common_openbsd.h` is the OpenBSD-specific shared support layer for syzkaller executor and generated C reproducers. It implements the small set of OpenBSD pseudo-syscalls and sandbox helpers needed to open PTYs, configure tap devices for packet injection, emit/extract Ethernet/TCP traffic, and run tests under either no sandbox or a setuid sandbox.

## Important APIs, Types, And Functions

- `syz_open_pts()` uses `openpty()` to allocate a master/slave pair, duplicates the master fd upward to lower collision risk with fuzzer-generated closes, and returns the slave fd.
- `tunfd` is the process-global fd for the active tap device.
- TUN/TAP constants define per-proc tap names and deterministic local/remote MAC, IPv4, and IPv6 addresses. The OpenBSD implementation supports up to `MAX_TUN` tap instances and derives names such as `/dev/tap%d` and `tap%d`.
- `vsnprintf_check()` and `snprintf_check()` are bounded formatting helpers that fail if generated command strings do not fit their fixed buffers.
- `execute_command()` prepends a fixed PATH and runs `ifconfig`, `arp`, and `ndp` commands via `system()`, optionally treating failure as fatal.
- `initialize_tun(int tun_id)` destroys any old tap instance, opens the requested `/dev/tap%d`, remaps it to fd `200`, configures MAC/IP addresses, and populates ARP/NDP neighbors.
- `syz_emit_ethernet()` writes raw packet data to `tunfd`.
- `read_tun()` reads from `tunfd`, treating `EAGAIN` as no packet.
- `struct tcp_resources` plus `syz_extract_tcp_res()` parse one Ethernet frame and return adjusted TCP sequence and acknowledgement values.
- `sandbox_common()` applies minimal resource limits and, in non-threaded mode, calls `setsid()`.
- `do_sandbox_none()` runs `sandbox_common()`, optional tap initialization, and `loop()`.
- `wait_for_loop()` and `do_sandbox_setuid()` fork a child, initialize tap support, resolve the `nobody` account, drop groups/gid/uid, and run `loop()` in the child.

## Control Flow

The non-sandbox path is direct: `do_sandbox_none()` applies resource limits, initializes tap injection for `procid` when enabled, and enters the generated `loop()`.

The setuid path forks first. The parent waits for the loop child with `waitpid()`, while the child applies `sandbox_common()`, sets up the tap interface while still privileged, switches to the `nobody` user/group with empty supplementary groups, then enters `loop()` and exits through `doexit()` if `loop()` returns.

Network injection control flow is command-driven rather than netlink-driven. `initialize_tun()` formats device/interface names, destroys previous state, opens the tap device, remaps the fd, and executes `ifconfig`, `arp`, and `ndp` commands to prepare layer-2 and layer-3 state. Generated pseudo-syscalls then use `syz_emit_ethernet()` and `syz_extract_tcp_res()` against the global fd.

## State And Persistence Behavior

The main process state is `tunfd`, remapped to fd `200` to keep it above normal generated fd ranges and consistent with syzkaller fd assumptions. The system state is the OpenBSD tap interface and static ARP/NDP entries. `initialize_tun()` tries to destroy a prior tap interface before opening and configuring the new one, but there is no comprehensive reset routine in this header.

Resource limits are process-local: memlock, file size, stack, core, and nofile are capped in `sandbox_common()`. The setuid sandbox persists the dropped credentials for the test child only.

## Dependencies And Integration Points

The file relies on common executor symbols such as `procid`, `loop()`, `debug`, `debug_dump_data`, `fail`, `failmsg`, `doexit`, and compile-time feature macros. It uses OpenBSD libc and system headers including `openpty`, `ifconfig`-visible tap devices, `arp`, `ndp`, `<netinet/ip.h>`, `<netinet/ip6.h>`, `<netinet/tcp.h>`, and `<netinet/if_ether.h>`.

The generated syzlang side must know the same tap fd behavior, address patterns, and TCP resource structure layout. Unlike the Linux version, OpenBSD setup delegates interface configuration to userland tools through `system()` with an explicit PATH.

## Risks And Edge Cases

- `execute_command()` uses a 128-byte command payload after the PATH prefix. New longer commands must either increase `COMMAND_MAX_LEN` or risk fatal formatting failure.
- The tap interface id must be in `[0, MAX_TUN)`, so `procid` mapping must remain bounded by the caller.
- `initialize_tun()` only returns gracefully for missing tap devices in csource mode; executor mode treats open failure as fatal.
- IPv6 parsing in `syz_extract_tcp_res()` does not skip extension headers.
- The Ethernet type branch treats every non-IPv4 frame as IPv6-shaped and then rejects if lengths/protocol do not match.
- Static ARP/NDP entries and tap interfaces may remain if the process exits before cleanup.
- `do_sandbox_setuid()` assumes a `nobody` passwd entry exists.

## Test Signals

- Successful tap setup is visible through `ifconfig tapN`, static IPv4/IPv6 addresses, and ARP/NDP entries.
- `syz_emit_ethernet()` should return the number of bytes written when `tunfd` is valid.
- `syz_extract_tcp_res()` should return `0` and write network-order adjusted `seq`/`ack` for valid IPv4/IPv6 TCP frames, and `-1` for no packet, malformed Ethernet/IP/TCP headers, or unsupported protocols.
- Sandbox behavior is indicated by child exit status in setuid mode and by expected `RLIMIT_*` values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_openbsd.h -->
