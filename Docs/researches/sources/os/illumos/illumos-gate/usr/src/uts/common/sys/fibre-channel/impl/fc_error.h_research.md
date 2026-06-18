# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_error.h

Defines common Fibre Channel return codes, packet states, packet reason codes, packet actions, and explanation values shared by FCA, fctl/fp, and ULP layers. General results include `FC_SUCCESS`, `FC_FAILURE`, allocation/packet/offline errors, ELS and transport errors, busy states, login/reset errors, and NPIV-specific errors.

Packet classification is split into `pkt_state` values such as `FC_PKT_SUCCESS`, `FC_PKT_TIMEOUT`, `FC_PKT_*_RJT`, and `FC_PKT_*_BSY`, then state-specific `FC_REASON_*`, `FC_ACTION_*`, and `FC_EXPLN_*` values. These constants are consumed by packet error translation helpers exposed through FCA/ULP interfaces.

This file is a vocabulary header, not an implementation header. Its values are part of cross-module behavior and should be extended carefully because callers may persist or expose them through ioctl error paths.
