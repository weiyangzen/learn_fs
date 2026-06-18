<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_linux.h -->
# sources/test-tools/syzkaller/executor/common_linux.h

## Purpose

`common_linux.h` is the Linux-specific shared executor/csource support layer for syzkaller. It provides feature-gated helpers used by generated pseudo-syscalls, sandbox entry points, network and device environment setup, repeat-mode cleanup, kernel instrumentation setup, and Linux-only emulation surfaces such as TUN/TAP, raw USB gadget, Bluetooth VHCI, io_uring/ublk, FUSE, BTF, KVM, and filesystem-image mounting.

The file is intentionally conditional. Most blocks are compiled when `SYZ_EXECUTOR` is enabled or when a generated C reproducer references the corresponding `__NR_syz_*` pseudo-syscall or feature macro. That lets the same implementation serve both the full executor and minimized reproducers without pulling every Linux subsystem into every binary.

## Important APIs, Types, And Functions

Core synchronization and utilities:

- `event_t`, `event_init`, `event_reset`, `event_set`, `event_wait`, `event_isset`, and `event_timedwait` implement a tiny futex-backed event primitive for threaded executor operation.
- `write_file()` formats and writes small control values into procfs/sysfs/debugfs files. It is used throughout feature setup and sandbox initialization.
- `runcmdline()` runs shell commands for the few setup paths that use existing tools, notably NIC VF setup and swap setup.

Netlink and networking:

- `struct nlmsg`, `netlink_init`, `netlink_attr`, `netlink_nest`, `netlink_done`, `netlink_send_ext`, `netlink_send`, and `netlink_query_family_id` form the local netlink message builder/sender used by route, generic-netlink, devlink, wireguard, nl80211, and nl802154 setup.
- Link construction helpers include `netlink_add_device`, `netlink_add_veth`, `netlink_add_xfrm`, `netlink_add_hsr`, `netlink_add_linked`, `netlink_add_vlan`, `netlink_add_macvlan`, `netlink_add_geneve`, `netlink_add_ipvlan`, `netlink_device_change`, `netlink_add_addr4`, `netlink_add_addr6`, and `netlink_add_neigh`.
- `initialize_tun()` repairs `/dev/net/tun`, creates `syz_tun`, assigns stable fd `200`, configures static IPv4/IPv6 addresses, permanent neighbors, and a fixed MAC.
- `read_tun()`, `flush_tun()`, `syz_emit_ethernet()`, and `syz_extract_tcp_res()` implement network injection and TCP sequence/ack extraction.
- `initialize_netdevices()` creates a rich test topology in the sandbox namespace: bridges, veth pairs, bonds, teams, hsr, xfrm, virt_wifi, vlan, macvlan, ipvlan, macvtap, macsec, geneve, netdevsim, wireguard, and several existing tunnel devices.
- `initialize_netdevices_init()` configures init-namespace-only devices such as NETROM/ROSE and discovers VF passthrough devices through `find_vf_interface()`.
- `netlink_wireguard_setup()` configures three wireguard peers with deterministic keys, ports, endpoints, and allowed IP halves.
- `initialize_devlink_pci()` moves a devlink PCI instance into the executor namespace and renames devlink ports.
- Wi-Fi support uses `hwsim80211_create_device`, `initialize_wifi_devices`, `nl80211_set_interface`, `nl80211_join_ibss`, `nl80211_setup_ibss_interface`, `await_ifla_operstate`, `syz_80211_inject_frame`, and `syz_80211_join_ibss`.
- IEEE 802.15.4 setup is in `setup_802154()`.

Pseudo-syscall shims and device emulation:

- USB pseudo-syscalls are included through `common_usb_linux.h` when USB support is needed.
- `syz_usbip_server_init()` creates a UNIX socket pair, allocates a per-proc VHCI port, writes the attach request to `/sys/devices/platform/vhci_hcd.0/attach`, and returns the server side.
- `initialize_vhci()`, `process_command_pkt()`, `event_thread()`, and `syz_emit_vhci()` emulate enough Bluetooth HCI/VHCI state to make Bluetooth socket descriptions reachable.
- `syz_open_dev()`, `syz_open_procfs()`, `syz_open_pts()`, `syz_init_net_socket()`, `syz_socket_connect_nvme_tcp()`, `syz_genetlink_get_family_id()`, `syz_memcpy_off()`, `syz_create_resource()`, `syz_pidfd_open()`, `syz_pkey_set()`, and `syz_kfuzztest_run()` are Linux pseudo-syscall helpers exposed to generated programs.
- `syz_clone()` and `syz_clone3()` clear `CLONE_VM`, set clone-in-progress state when segv handling is compiled in, and make child processes sleep briefly before plain `exit`.

Storage, filesystem, and kernel service helpers:

- `setup_loop_device()`, `reset_loop_device()`, `syz_read_part_table()`, and `syz_mount_image()` decompress syzkaller compressed images into memfd-backed loop devices, trigger partition scanning, mount filesystems, and normalize dangerous mount options.
- KVM setup is delegated to architecture headers such as `common_kvm_amd64.h`, `common_kvm_arm64.h`, `common_kvm_ppc64.h`, and related files.
- `read_btf_vmlinux()` and `syz_btf_id_by_name()` parse `/sys/kernel/btf/vmlinux` directly to resolve BTF type IDs by name.
- io_uring and ublk support defines local copies of ring offsets, CQE/SQE structures, ublk control/queue structures, and helpers `syz_io_uring_setup`, `syz_io_uring_submit`, `syz_io_uring_complete`, `syz_io_uring_modify_offsets`, `syz_ublk_setup_io_uring`, `syz_ublk_add_dev`, `syz_ublk_setup_queues`, and `syz_ublk_process_io`.
- FUSE support defines FUSE opcodes and headers, `struct syz_fuse_req_out`, `fuse_send_response()`, and `syz_fuse_handle_req()` for selecting fuzzer-supplied responses per request opcode.

Sandbox and repeat-mode APIs:

- `sandbox_common()` applies parent-death signaling, saves the initial network namespace fd, sets resource limits, unshares namespaces, makes mounts private, and writes IPC sysctls.
- `sandbox_common_mount_tmpfs()` builds a tmpfs-backed chroot/newroot tree, bind-mounts selected system paths, mounts proc/sys/debug/smack/binfmt/syz-inputs as appropriate, initializes cgroup bind mounts, pivots/chroots, and sets up gadgetfs, binderfs, and fusectl.
- `do_sandbox_none()`, `do_sandbox_setuid()`, `do_sandbox_namespace()`, and `do_sandbox_android()` sequence environment setup, capabilities, network namespaces, device initialization, and privilege dropping for each sandbox mode.
- `drop_caps()` removes selected capabilities, primarily `CAP_SYS_PTRACE` and `CAP_SYS_NICE`.
- Android-specific helpers `getcon`, `setcon`, and `setfilecon` manipulate SELinux state without libselinux and `do_sandbox_android()` optionally switches between untrusted app and system credentials.
- `remove_dir()` recursively unmounts and deletes tmp directories while handling busy mounts, immutable flags, and read-only filesystem cases.
- Repeat-mode hooks include `setup_loop()`, `reset_loop()`, `setup_test()`, `close_fds()`, and `kill_and_wait()`.

Feature setup and diagnostics:

- `setup_cgroups`, `mount_cgroups`, `mount_cgroups2`, `setup_cgroups_loop`, `setup_cgroups_test`, and `initialize_cgroups` prepare v1/v2 cgroups and per-test cgroup symlinks.
- `checkpoint_net_namespace()` and `reset_net_namespace()` snapshot and restore iptables, ip6tables, arptables, and ebtables state through locally defined userspace ABI structures.
- `setup_fault()` and `inject_fault()` configure kernel fault-injection files; `fault_injected()` checks and resets fail-nth state.
- `setup_leak()` and `check_leaks()` drive kmemleak with delayed rescans to reduce false positives.
- Other setup functions include `setup_binfmt_misc()`, `setup_kcsan()`, `setup_usb()`, `setup_sysctl()`, and `setup_swap()`.

## Control Flow

The file is not a single control path; it is a library of feature setup routines and pseudo-syscall implementations. The broad executor boot flow compiles into the sandbox entry selected by flags:

1. A sandbox entry (`do_sandbox_none`, `do_sandbox_setuid`, `do_sandbox_namespace`, or `do_sandbox_android`) forks/clones where needed and establishes parent/child ownership through `wait_for_loop()`.
2. It initializes privileged early devices such as VHCI, calls `sandbox_common()`, and optionally drops capabilities or switches credentials.
3. It sets up the initial namespace artifacts: cgroups, init-net devices, a new network namespace, ping group sysctl, devlink PCI, TUN/TAP, virtual network devices, Wi-Fi hwsim, tmpfs/chroot/binder/fuse/gadget mounts.
4. It enters the generated executor `loop()`.

Repeat-mode control flow wraps each program execution:

1. `setup_loop()` may create per-proc cgroups and checkpoint netfilter tables.
2. `setup_test()` sets parent-death behavior, process group, cgroup symlinks, OOM score, TUN drain, and binderfs symlink.
3. The generated program runs pseudo-syscalls and real syscalls.
4. `reset_loop()` clears per-proc loop devices and restores netfilter tables.
5. `close_fds()` closes generated fds including USB emulation fds so coverage can flush and event loops can exit.
6. `kill_and_wait()` escalates stuck test processes and aborts FUSE connections when ordinary SIGKILL waiting is insufficient.

Pseudo-syscalls are generally short wrappers around Linux ABI surfaces. Some have multi-step protocols: USB raw-gadget connection loops over EP0 control events until configuration completes; io_uring setup maps shared rings and exposes pointers to syzlang; ublk setup submits io_uring commands and maps queue buffers; FUSE handling reads a request and dispatches by opcode to a fuzzer-provided response header.

## State And Persistence Behavior

Persistent process globals include:

- `tunfd`, fixed at fd `200` after setup.
- `kInitNetNsFd`, fixed at fd `201` for initial net namespace access.
- `vhci_fd`, fixed at fd `202` after VHCI setup.
- `nlmsg` and `nlmsg2`, shared stack-like netlink buffers.
- Netfilter checkpoint arrays `ipv4_tables`, `ipv6_tables`, `arpt_tables`, and `ebt_tables`.
- `vf_intf`, used to carry VF passthrough discovery into setup.
- `port_alloc[2]` in `syz_usbip_server_init()`, static per process for USB/IP port allocation.
- The static BTF vmlinux cache in `read_btf_vmlinux()`.

Kernel and filesystem state is intentionally mutated. The file writes sysctls, creates network devices and neighbors, mounts cgroups and tmpfs, creates binderfs/gadgetfs/fusectl mounts, configures raw-gadget permissions, enables swap, registers binfmt_misc handlers, changes kmemleak and KCSAN debug knobs, creates loop-device associations, and may attach usbip devices. Some state is per namespace and cleaned by namespace teardown; other state is global or sticky, such as netdevsim devices, sysctls, binfmt_misc entries, swap files, and debugfs knobs.

The cleanup/reset paths are partial but deliberate. Netfilter tables are checkpointed/restored, loop devices are cleared, TUN queues are flushed, cgroups are reused per proc, and tmp directories are aggressively unmounted/deleted. The design accepts that some setup calls can fail on older or differently configured kernels and logs optional failures instead of aborting, while fatal setup dependencies use `fail()` or `failmsg()`.

## Dependencies And Integration Points

This header depends on executor-provided symbols and macros such as `SYZ_EXECUTOR`, `flag_*` feature flags, `procid`, `debug`, `debug_dump_data`, `fail`, `failmsg`, `exitf`, `doexit`, `sleep_ms`, `current_time_ms`, `kMaxThreads`, `kCoverSize`, `syscall_timeout_ms`, `loop()`, and optional `cover_reset`.

It integrates with:

- Linux UAPI headers for netlink, rtnetlink, nl80211, if_tun, if_link, genl, loop, KVM, rfkill, USB, capabilities, sched, cgroups, io_uring-compatible structures, and BTF-compatible copied structs.
- syzkaller headers `common_usb_linux.h`, `common_zlib.h`, architecture-specific `common_kvm_*.h`, and Android seccomp support.
- syzlang descriptions that know fixed names, fds, addresses, handles, and device names, including `syz_tun`, `wlan0/1`, `wg0/1/2`, Bluetooth handles `200/201`, `/dev/loop<procid>`, and many virtual netdevice names.
- Kernel configuration and runtime features such as TUN, netdevsim, wireguard generic netlink, mac80211_hwsim, nl802154, dummy_hcd/raw-gadget, vhci, debugfs, kmemleak, fault injection, cgroup v1/v2, binderfs, fusectl, KCSAN, binfmt_misc, KVM, ublk, io_uring, and USB/IP VHCI.

## Risks And Edge Cases

- Many helper structures mirror Linux UAPI manually. Kernel ABI drift can silently break io_uring, ublk, BTF, netfilter, ebtables, FUSE, USB raw-gadget, and devlink interactions.
- `struct nlmsg` has a fixed 4096-byte buffer and nesting depth 8. The code fails on overflow/bad nesting but large future netlink messages may need explicit resizing.
- Global or sticky host state is modified. netdevsim devices, debugfs knobs, binfmt_misc entries, swap, sysctls, and some device moves can outlive one executor process.
- The setup path intentionally ignores optional failures. That improves portability but can reduce test reachability without making the failure obvious unless debug logs are examined.
- Namespace switching via `setns()` can fail if another thread closes fds; the code treats restoration failure as fatal.
- Several helpers use `sprintf`/fixed buffers with controlled internal strings, but additions should preserve bounds assumptions.
- `read_btf_vmlinux()` caches a fixed 10 MiB BTF blob and has a benign race; larger kernels or short reads at the limit return failure.
- `syz_io_uring_complete()` and `syz_io_uring_submit()` trust ring pointers and do not validate empty/full rings, by design for fuzzing.
- `syz_mount_image()` appends mount options into a 256-byte buffer and only logs when generated options are too large; malformed options are expected in fuzzing but can affect outcome clarity.
- Android sandboxing is architecture-sensitive and relies on direct SELinux xattr/context manipulation.
- `remove_dir()` is intentionally aggressive around mounts and immutable flags; it is risky to reuse outside a disposable executor tmp tree.

## Test Signals

Useful validation signals include:

- Feature-probe failures returned from setup functions, e.g. `setup_fault`, `setup_leak`, `setup_usb`, `setup_swap`, `setup_802154`, `setup_kcsan`, and `setup_binfmt_misc`.
- Debug lines from netlink setup, TUN initialization, wireguard setup, Wi-Fi hwsim setup, devlink port initialization, USB/IP attach, raw-gadget USB, VHCI, io_uring/ublk, FUSE, and mount-image helpers.
- Kernel-visible artifacts: presence of `syz_tun`, virtual netdevices, configured `wlan0/wlan1`, `/syzcgroup/*`, `/dev/binderfs`, `/dev/gadgetfs`, `/sys/fs/fuse/connections`, `/proc/sys/fs/binfmt_misc` registrations, raw-gadget permissions, swap activation, and loop device cleanup.
- Repeat-mode isolation checks: no stale packets after `flush_tun`, netfilter tables restored after `reset_net_namespace`, per-test cgroup symlinks exist, and loop device `LOOP_CLR_FD` succeeds.
- Pseudo-syscall return values: fd-returning helpers return nonnegative fds, generated response helpers return `0`, extraction helpers write expected sequence/ack values, and error paths preserve `errno` where documented.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_linux.h -->
