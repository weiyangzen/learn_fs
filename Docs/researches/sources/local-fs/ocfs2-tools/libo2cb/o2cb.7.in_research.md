# File Research: sources/local-fs/ocfs2-tools/libo2cb/o2cb.7.in

## Purpose

Manual page source describing the O2CB cluster stack used by OCFS2.

## Main Contents

- Defines O2CB as the default in-kernel OCFS2 cluster stack with o2nm, o2hb, o2net, o2dlm, and dlmfs.
- Explains cluster configuration through `o2cb(8)`, `/etc/ocfs2/cluster.conf`, and `/etc/sysconfig/o2cb`.
- Describes local heartbeat and global heartbeat modes and the operational tradeoff between per-mount heartbeat threads and shared configured heartbeat devices.
- Covers required kernel sysctls: `panic_on_oops` and `panic`.
- Notes firewall/network requirements for O2CB private network traffic.
- Gives a detailed disk heartbeat explanation: sequence-number writes, timeout detection, self-fencing, and global heartbeat tolerance across multiple heartbeat regions.
- Documents online modification of nodes and heartbeat regions in global heartbeat mode.
- Provides getting-started examples for formatting global heartbeat volumes, onlining cluster stack, formatting volumes, converting existing volumes, listing mounted volumes, checking status, and offlining/unloading.

## Dependencies and Integration

- Template includes `@VERSION@` substitution from the build/manpage generation process.
- Cross-references `o2cb(8)`, `o2cb.sysconfig(5)`, `ocfs2.cluster.conf(5)`, and `o2hbmonitor(8)`.

## Research Notes

- This file is documentation, not executable code, but captures intended cluster semantics that `libo2cb` implements.
