# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/linkapp.h

## Role

`linkapp.h` is an older Fibre Channel link application payload header. It defines a smaller set of well-known addresses, link application opcodes, basic accept/reject payloads, service parameters, WWN representation, login/RLS/LOGO/reject payloads, and reject reason/explanation codes.

## Definitions

- Defines well-known fabric addresses for multicast, management, time, name, fabric controller/F-port, and broadcast.
- Defines opcodes `LA_RJT`, `LA_ACC`, `LA_LOGI`, `LA_LOGO`, `LA_RLS`, and `LA_IDENT`.
- Defines `ba_acc_t` and `ba_rjt_t`, with BA_RJT reason/explanation constants.
- Defines common service parameters, service parameter block, `la_wwn_t`, and NAA id constants.
- Defines `la_logi_t`, `la_rls_t`, `la_rls_reply_t`, `la_logo_t`, `la_logo_reply_t`, and `la_rjt_t`.
- Defines LA_RJT reason and explanation constants, including options, initiator/recipient, data field size, concurrent, credit, invalid port/node WWN, invalid common service, and insufficient resources.

## Relationship To `fcal_linkapp.h`

This is a smaller predecessor/variant of the FC-AL link application header. Newer FC-AL payloads and ELS opcodes are in `fcal_linkapp.h`.
