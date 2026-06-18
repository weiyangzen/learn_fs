# sources/security-integrity/selinux/libsepol/include/sepol/port_record.h

Purpose: Declares the public record/key API for TCP/UDP/DCCP/SCTP port contexts.

Important APIs and types: Opaque `sepol_port_t` and key type; protocol constants; key create/unpack/extract/free; compare helpers; protocol, low/high port, single-port/range, context accessors; create/clone/free.

Control flow: Keys identify low/high port plus protocol; records attach a context. Collection APIs in `ports.h` search or modify policydb port ocontexts.

State and persistence: Records own scalar range/protocol values and context pointer/copy semantics through implementation.

Dependencies and integration points: Depends on context records and handles; maps to `OCON_PORT`.

Risks: Range overlap, protocol constants, and low/high ordering must match kernel policy semantics.

Test signals: Protocol string mapping, range/single-port setters, invalid protocol/range cases, and policydb query/modify validate it.
