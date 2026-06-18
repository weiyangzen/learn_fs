# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_fcaif.h

Defines the Fibre Channel adapter driver interface consumed by the transport framework. It declares FCA module revision levels, state-change values, port-management flags, reset command codes, port-management command codes, and capability string names.

Core data structures are `fc_fca_bind_info_t`, `fc_fca_port_info_t`, `fc_fca_pm_t`, `fc_fca_p2p_info_t`, and especially `fc_fca_tran_t`. `fc_fca_tran_t` is the adapter operations vector for binding/unbinding ports, packet initialization, ELS send, capability get/set, loop-map retrieval, transport, unsolicited buffer management, abort/reset, port management, FCA device lookup, and notifications.

Exports include `fc_fca_init`, `fc_fca_attach`, `fc_fca_detach`, and error translation helpers. This file is the main fctl-to-HBA-driver contract; changes affect every FCA driver and the fp/fctl framework.
