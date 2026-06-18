# File Research: sources/local-fs/ocfs2-tools/ocfs2_controld/main.c

`main.c` is the `ocfs2_controld` daemon core. It owns the poll-loop client table, signal pipe, listening socket for `mount.ocfs2` clients, debug ring buffer, daemonization/lockfile handling, stack verification, protocol negotiation, and startup/shutdown sequence.

Startup initializes o2cb, verifies the built daemon stack matches configured stack, optionally daemonizes, raises scheduler priority, lowers OOM score, sets up signal handling, cluster stack, checkpoint service, node protocol checkpoint, daemon CPG, DLM control, kernel control device, and client listener. CPG join completion negotiates or reads global daemon/filesystem protocol versions.

Client protocol handling supports mount, mount-result, unmount, list clusters, list filesystems, and debug dump messages. It validates filesystem type and cluster name before delegating to `mount.c`.

Risk areas include global mutable state, fixed-size debug buffer protocol chunking, fail-stop behavior while mounts exist, PID lock under `/var/run`, and protocol negotiation depending on checkpoint availability and format correctness.
