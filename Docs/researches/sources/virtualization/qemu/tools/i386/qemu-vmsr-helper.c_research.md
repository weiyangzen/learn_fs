# File Research: sources/virtualization/qemu/tools/i386/qemu-vmsr-helper.c

## Purpose
Privileged helper process that lets QEMU read a narrow allowlist of Intel RAPL MSRs through a Unix socket. It is intended to expose virtual RAPL MSR values while isolating raw MSR access in a helper with `CAP_SYS_RAWIO`.

## Main Behavior
- Computes default socket and pidfile paths under QEMU local state.
- Verifies the host CPU vendor is Intel via CPUID.
- Verifies Intel RAPL is enabled through `/sys/class/powercap/intel-rapl/enabled`.
- Listens on a Unix socket or systemd socket activation fd.
- Accepts clients, obtains peer PID, and serves requests in coroutines.
- Each request is three `uint32_t` values: MSR register, CPU ID, and TID.
- Only allows RAPL MSRs listed in `rapl-msr-index.h`.
- Reads `/dev/cpu/<cpu>/msr` with `pread()`.
- Verifies requested TID belongs to the peer process by checking `/proc/<pid>/task/<tid>`.
- Replies with a `uint64_t` MSR value or zero on failed/unauthorized reads.

## CLI and Runtime
Options include help/version, daemon mode, pidfile, socket path, trace settings, verbose errors, and optional user/group flags when libcap-ng is enabled. The main loop handles SIGTERM/SIGINT/SIGHUP and closes the server socket on termination.

## Security Model
- Restricts MSR reads to four package/RAPL registers.
- Checks peer task ownership for the supplied TID.
- Can integrate with libcap-ng to retain only `CAP_SYS_RAWIO`.
- Rejects relative socket paths.
- Supports socket activation but only one inherited fd.

## Filesystem/Storage Relevance
Indirect. This is virtualization host-helper infrastructure, not filesystem logic. It does interact with Linux device files and `/proc`/`/sys` paths to safely proxy privileged CPU telemetry into QEMU.

## Notable Limitations
- RAPL and CPU checks happen before option parsing.
- `uid`/`gid` parsed under libcap-ng are stored but this file’s `drop_privileges()` only clears/adds capabilities and does not itself switch user/group.
