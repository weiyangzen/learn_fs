# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fcal_linkapp.h

## Role

`fcal_linkapp.h` defines FC-AL link application opcodes, events, well-known addresses, service parameter formats, World Wide Name formats, and ELS payload structures.

## Link Application ABI

- Defines `MAX_FCODE_SIZE`, well-known fabric addresses, and many ELS opcodes such as reject, accept, PLOGI/FLOGI/LOGO, RLS, ECHO, RRQ, PRLI/PRLO, SCN, TPLS, GPRLO, GAID/FACT/FDACT, QoSR, PDISC/FDISC/ADISC, plus SMCC-specific display/identify values.
- Defines sysevent strings for FCAL device insertion and removal.
- Defines BA_ACC and BA_RJT payloads and reason/explanation codes.
- Defines common service parameters, 16-byte service parameter blocks, `la_wwn_t`, WWN size, and NAA id values.
- Defines ELS login payload/reply, RLS request/reply, LOGO request/reply, RRQ request/reply, PRLI/PRLO request/reply, PDISC request/reply, ADISC request/reply, identify request/reply, and link application reject payload.

## Notes

The header contains a historical malformed macro line `#define LA_RJT_ INVALID_SEQ_ID 0x21`; consumers likely avoid it or rely on compiler parsing behavior. It should be treated as part of the source as-is, not silently normalized.
