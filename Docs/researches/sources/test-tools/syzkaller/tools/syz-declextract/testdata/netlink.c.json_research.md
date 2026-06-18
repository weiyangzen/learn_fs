# sources/test-tools/syzkaller/tools/syz-declextract/testdata/netlink.c.json

Purpose: this golden JSON describes expected generic netlink extraction for `netlink.c`.

Important structure: top-level keys are `functions`, `consts`, `structs`, `netlink_families`, and `netlink_policies`. Functions include atomic helpers, `foo_cmd`, `bar_cmd`, and split-op callbacks. Constants include UAPI family command/attribute values plus local nested/no-policy command constants. Structs include `netlink_foo_struct1` size 12 align 4 and `netlink_foo_struct2` size 24 align 8.

Control-flow and integration: family records cover normal ops, split ops, no-ops family, and no-policy family. Policy records represent scalar, string length, nested policy, and `sizeof`-derived binary payload lengths.

State and persistence: static test cache. Its line numbers, constants, and policy shapes must match the C fixture.

Risks and test signals: strong signal for netlink-family extraction and UAPI versus local constant treatment. It is sensitive to schema naming and nested policy representation.
