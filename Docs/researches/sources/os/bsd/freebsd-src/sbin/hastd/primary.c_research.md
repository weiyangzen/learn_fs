# File Research: sources/os/bsd/freebsd-src/sbin/hastd/primary.c

Read completely: 2450 lines.

This file implements the primary-role worker. It exposes the GEOM Gate provider to the kernel, forwards I/O to local and remote components according to the selected replication mode, maintains the activemap, performs synchronization, reconnects to the secondary, and handles live primary configuration reloads.

Key responsibilities:
- Creates parent/child socketpair channels for control, events, and connection requests, then forks the primary worker.
- In the child, cleans descriptors, reinitializes logging, reads metadata, initializes activemap and range locks, opens `/dev/ggctl`, creates or recovers `hast/<provider>`, drops privileges, and starts worker threads.
- Maintains a fixed pool of 256 `hio` request objects with per-component error slots and queue linkage.
- Runs queues for free requests, local send, remote send, remote receive, done completion, and synchronization.
- Receives GEOM Gate I/O (`BIO_READ`, `BIO_WRITE`, `BIO_DELETE`, `BIO_FLUSH`) and dispatches it to local and/or remote components.
- Implements replication semantics: async can complete writes after local success, memsync completes after local success plus remote receive acknowledgment, and fullsync waits for final remote completion.
- Tracks dirty ranges in the activemap, writes it after dirty/clean transitions, and uses range locks to serialize regular writes against synchronization.
- Performs two-stage primary-to-secondary handshake, validates data/extent sizes, negotiates protocol version, exchanges counters/resource UUID, receives remote activemap data, detects split-brain messages, and starts synchronization.
- Runs a guard thread for signals and periodic reconnection.
- Supports live reload of remote/source address, replication, checksum, compression, timeout, hook path, and metaflush.

Important interactions:
- Depends on GEOM Gate ioctls for virtual block-device I/O.
- Uses `metadata.c` for persistent resource identity/counters and `activemap` for dirty extent tracking.
- Uses `proto_*` and `hast_proto_*` for remote communication.
- Uses `event_send()` for connect/disconnect/sync/split-brain notifications.
- Uses `ctrl_thread()` for child control messages and `primary_config_reload()` for reload commands.

Reliability and security notes:
- Remote connection access is protected by per-component rwlocks; metadata counters are protected by `metadata_lock`.
- Local reads can fall back to remote reads when appropriate.
- The synchronization source is determined by local/remote counters and remote handshake state outside this file’s visible helpers, then used to read from the up-to-date side and write to the stale side.
- If the remote disconnects, the primary bumps local counters on subsequent writes to preserve divergence tracking.
- Many fatal paths destroy the GEOM Gate provider before exiting; worker restart is supervised by the parent daemon.
