# sources/test-tools/syzkaller/tools/syz-declextract/testdata/include/uapi/netlink_family.h

Purpose: this UAPI fixture defines a hypothetical generic netlink family command/attribute namespace and payload structs.

Important APIs and flow: `enum netlink_foo_cmds` defines FOO and BAR commands. `enum netlink_foo_attrs` defines non-dense attributes with `NETLINK_FOO_ATTR3 = NETLINK_FOO_ATTR2 + 3`. `struct netlink_foo_struct1` has three ints, and `netlink_foo_struct2` is a typedef struct with three doubles.

State and persistence: declarations only.

Dependencies and integration: included by `netlink.c` and reflected in netlink policy extraction. The non-dense enum tests attribute numbering and constant inclusion.

Risks: synthetic family data is small and omits many real netlink validation features.

Test signals: paired JSON should report command and attribute constants plus struct sizes/alignments for both payload types.
