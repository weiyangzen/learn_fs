# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fctl_private.h

Defines private fctl state not intended for other modules. It includes hash table sizes/functions for PWWN, D_ID, and NWWN, FC-4 bitmap helpers, invalid error sentinels, translated ULP state-change values, ULP attach retry count, NPIV limits, and ULP port lifecycle flags.

Major structures include `fc_ulp_ports_t`, `fc_ulp_module_t`, `fc_fca_port_t`, `timed_counter_t`, `fc_remote_node_t`, `fc_remote_port_t`, global NWWN hash entries, packet error mapping structures, and `fc_local_port_t`. The comments document lock ordering, reference counts, login state, relogin suppression, remote-node/remote-port relationships, job queues, state-change nesting, port power management, unsolicited buffers, orphan lists, HBA attributes, and NPIV bookkeeping.

`fc_local_port_t` is the fp per-instance soft state. It ties together FCA handle/vector, local state/topology, job queue, wait queue, remote-port hash tables, taskq, timeouts, power management, FC-4 type registration, fabric data, and NPIV port lists. The file ends with private/static prototypes for fctl child management, ULP port registration, host name-service values, link reset completion, error decoding, DMA attribute initialization, and NPIV create/delete lookup.
