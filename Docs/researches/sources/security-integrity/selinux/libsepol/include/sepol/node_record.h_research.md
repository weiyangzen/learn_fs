# sources/security-integrity/selinux/libsepol/include/sepol/node_record.h

Purpose: Declares the public record/key API for IPv4/IPv6 node contexts.

Important APIs and types: Opaque `sepol_node_t` and key type; protocol constants `SEPOL_PROTO_IP4/IP6`; key create/unpack/extract/free; address/mask string and byte getters/setters; protocol get/set/string; context accessors; create/clone/free.

Control flow: Keys identify address, mask, and protocol; records carry the same plus a context. Collection APIs in `nodes.h` search or modify policydb node ocontexts.

State and persistence: Records own address/mask/context data; persistence requires policydb modification and write.

Dependencies and integration points: Depends on context records and handles; maps to `OCON_NODE` and `OCON_NODE6`.

Risks: Address byte order, family mismatch, and mask length validation are high-risk. String conversion must handle IPv4 and IPv6 consistently.

Test signals: IPv4/IPv6 string/byte round trips, protocol string mapping, invalid family/mask cases, and policydb query/modify are key tests.
