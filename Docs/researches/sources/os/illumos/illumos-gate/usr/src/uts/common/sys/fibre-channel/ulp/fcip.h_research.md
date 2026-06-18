# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/ulp/fcip.h

Defines private and protocol structures for the FCIP ULP that carries IP/ARP over Fibre Channel. It includes STREAMS module constants, MTU/packet sizing, multicast hash configuration, per-stream state `struct fcipstr`, DLPI address length, port attach information `fcip_port_info_t`, unsolicited buffer sizing, timeout/retry constants, routing/destination hash sizes, and taskq sizing.

`struct fcip` is the per-device state: devinfo/instance, sibling port, port state, ULP port info, FARP serialization, unsolicited buffer tokens/counts, destination and routing hash tables, local MAC/WWN/IP addresses, transmit/send-up caches, taskq/thread synchronization, broadcast D_ID, kstats, MIB-II counters, and CPR state.

The file also defines route and destination objects (`fcip_routing_table`, `fcip_dest`), transmit packet wrapper `fcip_pkt_t`, DLPI full address `fcipdladdr`, LLC/SNAP header, kstat layout, copy macros, FARP ELS request/reply codes and payload `la_els_farp_t`, FARP/InARP response lists, optional FC-PH network header, InARP packet structure, esballoc callback argument, send-up queue element, and FC-4 type bitmap helpers.
