# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fc_linkapp.h

Defines Link Application ELS opcode constants and common ELS/BLS payload structures. It includes PLOGI/FLOGI/LOGO/PRLI/PRLO/ADISC/PDISC/FDISC/RSCN/SCR/LINIT/RNID opcodes, BA_ACC/BA_RJT payloads, LOGO and ADISC payloads, ELS RJT payloads, and PRLI/PRLO service parameter layouts.

The file includes process login/logout service parameter flags such as `SP_OPA_VALID`, `SP_RPA_VALID`, and response-code masks. Like other FC wire headers, it uses endian-dependent bitfields.

This is a protocol layout header for ELS handling in fp/fctl and ULPs. It is most relevant when tracing login/logout, address discovery, and unsolicited ELS response paths.
