# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_portif.h

Defines internal fctl/fp port-driver interfaces. It contains orphan-scan and LOGO tolerance constants, name-server request flags, fp soft-state bits, fp option bits, power-management levels, and device-address helper macros.

The central type is `job_request_t`, used by the per-port job-handler thread. Job codes cover ULP attach, port startup/shutdown, map retrieval, PLOGI/LOGO, online/offline, unsolicited requests, name-server commands, link reset, ULP notification, and FCIO login/logout. Job flags control fctl async completion, fp async completion, and ULP notification cancellation.

Also defines `fc_port_clist_t`, `fctl_ns_req_t`, `fc_orphan_t`, DMA/no-DMA copy macros `FC_GET_RSP` and `FC_SET_CMD`, and a broad set of fctl prototypes for remote node/port lifecycle, job queueing, ULP attach/detach, port busy/idle, lookup tables, port-map filling, name-service commands, orphan handling, WWN utilities, timed counters, and NPIV adapter lookup.
