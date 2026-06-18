# File Research: sources/os/bsd/freebsd-src/sbin/hastd/secondary.c

`secondary.c` implements the worker process for a HAST resource running in secondary role. The parent creates control/event socketpairs, forks, keeps parent-side descriptors, and the child initializes logging, descriptors, local metadata, request pools, privilege dropping, the control thread, remote handshake, and then the receive/disk/send pipeline.

The remote initialization exchanges resource size, extent size, counters, resource UID, synchronization source, and active map data. It detects first-use resources, resource UID mismatch, primary-out-of-date, secondary-out-of-date, in-sync, impossible-counter cases, and split-brain. Split-brain sends an error response, emits `EVENT_SPLITBRAIN`, and exits.

Runtime I/O uses a fixed pool of 256 `struct hio` entries, each with a `MAXPHYS` data buffer. Three queues are coordinated by mutexes and condition variables: free, disk, and send. `recv_thread()` validates protocol headers, receives write data, counts stats, handles keepalives, and clones memsync write requests so the primary can get an early "received" reply plus the later disk-completion reply. `disk_thread()` clears the local active map on the first real request after the primary has received it, then performs `pread()`, `pwrite()`, `g_delete()`, and `g_flush()`. `send_thread()` serializes replies, includes read data only on successful reads, reports per-command errors, and recycles requests.

Security and correctness checks include sector-size alignment, nonzero length, `MAXPHYS` write/read limit, datasize bounds, command validation, privilege drop before steady-state service, and disconnect events on fatal protocol errors.
