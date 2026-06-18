# sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/netlink.h

Purpose: this fixture header defines enough generic netlink and netlink attribute policy types for declextract netlink-family tests.

Important APIs and flow: it declares NLA type enum values, `struct nla_policy` with type/validation/length and union members for masks, nested policies, and ranges, `NLA_POLICY_NESTED`, generic netlink permission flags, operation structs (`genl_ops`, `genl_split_ops`, `genl_small_ops`), and `struct genl_family` fields for family name, operation counts, policy, ops, small ops, and split ops.

State and persistence: static declarations only.

Dependencies and integration: includes `types.h` for fixed-width aliases and `ARRAY_SIZE`. Used by `netlink.c` to test policy extraction, nested policies, split ops, and family metadata.

Risks: `genl_family` contains a likely intentional typo field `mall_ops`; extraction code must rely on the fields it supports. The fixture models only the subset of kernel netlink metadata needed for tests.

Test signals: paired netlink JSON should expose policies, family records, command constants, callback functions, and struct sizes for UAPI payload types.
