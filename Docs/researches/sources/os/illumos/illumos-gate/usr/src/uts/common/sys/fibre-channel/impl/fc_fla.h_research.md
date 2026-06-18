# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_fla.h

Defines Fabric Loop Application payloads and constants. It covers SCR registration function codes, RSCN affected-address formats, `FLA_RR_TOV`, and structures for SCR requests/responses, RSCN payload headers, affected IDs, LINIT requests/responses, and loop-status requests/responses.

The structures use endian-dependent bitfields guarded by `_BIT_FIELDS_LTOH` / `_BIT_FIELDS_HTOL`, so they are wire-format sensitive. Consumers must not treat the bitfield layout as portable outside the illumos build configuration.

The file is used by fp/fctl discovery and state-change handling when registering for fabric notifications, processing RSCNs, and dealing with loop initialization/status ELS payloads.
