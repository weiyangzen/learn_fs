# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fctl.h

Defines shared fctl/fp transport structures and constants. It encodes local port state and link speed values in `fp_state`, helper masks for state and speed, notification flags, packet transport flags/classes, packet transport types, and trace logging flags.

The key type is `fc_packet_t`, the common exchange object passed between ULPs, fctl/fp, and FCA drivers. It contains command/response/data buffers, DMA handles/cookies, FC frame headers, completion callbacks, remote-port and FCA-private references, packet state/reason/action/explanation, residuals, unsolicited response token, and reserved fields including `pkt_ulp_rscn_infop`.

The file also defines T11 HBA speed/attribute constants, `fca_port_attrs_t`, unsolicited buffer `fc_unsol_buf_t`, trace queue/message structures, remote-port change type constants, trace utility prototypes, and WWN string conversion helpers.
