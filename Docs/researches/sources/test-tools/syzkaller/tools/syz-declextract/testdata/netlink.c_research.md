# sources/test-tools/syzkaller/tools/syz-declextract/testdata/netlink.c

Purpose: this fixture exercises generic netlink family, operation, split-operation, policy, nested-policy, and payload-size extraction.

Important APIs and flow: it defines local nested attr constants, nested and top-level `nla_policy` arrays with scalar, string, nested, and `sizeof`-based payload entries, a dump-only policy, and reject-all/forward-declared policies. It defines callback functions and `genl_ops` for `foo_family`, including doit and dumpit variants. It defines `bar_family` using `genl_split_ops` with pre/do/post callbacks, `noops_family` with no operations, and `nopolicy_family` with ops but no family policy.

State and persistence: static const arrays and family structs only.

Dependencies and integration: includes generic netlink fixture types and UAPI family constants. Paired JSON feeds declextract tests for `netlink_families` and `netlink_policies`.

Risks: pointer-to-policy and array-size inference are sensitive to C initializer forms. Non-dense attributes and local non-UAPI constants intentionally exercise include versus value emission decisions.

Test signals: golden JSON includes functions, constants, payload structs, families `BAR`, `NOOPS`, `foo family`, and `nopolicy`, and policy metadata.
