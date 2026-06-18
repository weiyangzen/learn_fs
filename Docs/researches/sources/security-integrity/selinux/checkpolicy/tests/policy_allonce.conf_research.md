# sources/security-integrity/selinux/checkpolicy/tests/policy_allonce.conf

## Purpose

`policy_allonce.conf` is a compact non-MLS SELinux policy source fixture that deliberately exercises many checkpolicy language constructs in one file. It is used by `test_roundtrip.sh` as the input for normal round-trip testing and optimized round-trip testing.

## Policy Surface

The fixture declares handle-unknown behavior, object classes, inherited common permissions, initial SIDs, default user/role/type rules, `policycap open_perms`, attributes, expandattribute directives, types with aliases, `typealias`, `typeattribute`, `typebounds`, booleans, tunables, TE rules, filename transitions, extended permissions, permissive and neveraudit declarations, roles, role attributes, role transitions, conditional blocks, optional/require syntax, users, constraints, validatetrans, SID contexts, filesystem labeling, genfs contexts, port/netif/node contexts, InfiniBand pkey contexts, and InfiniBand endport contexts.

## Control Flow And Integration

The file has no runtime control flow, but its declaration order and syntax variants feed the checkpolicy parser. In the test script it is compiled with default options and decompiled with `-b -F` into `policy_allonce.expected.conf`; it is also compiled/decompiled with `-S -O` and compared against `policy_allonce.expected_opt.conf`.

## State And Persistence

This is a declarative policy artifact. Persistent state exists only as the semantic policy compiled into `testpol.bin` during testing. The source intentionally uses aliases, wildcard permissions, CIDR node syntax, wildcard network interfaces, hex InfiniBand values, and unquoted root genfs paths to verify canonical persistence through the binary policy format.

## Dependencies And Integration Points

It depends on the checkpolicy grammar and libsepol decompiler behavior. It integrates directly with `policy_allonce.expected.conf`, `policy_allonce.expected_opt.conf`, and `test_roundtrip.sh`.

## Risks

Because this fixture covers many unrelated grammar features, a failure can be broad and requires diff inspection to isolate whether the parser, optimizer, serializer, or decompiler changed. The test is order-sensitive for canonical output. The file also contains old-style comments documenting expected normalization, such as `sameuser` expansion, quoted paths, CIDR normalization, and hex-to-decimal conversion.

## Test Signals

The key signal is a clean `diff -u` against both expected files after the compile/decompile cycle. Important semantic signals include expansion of set-based rules, preservation of aliases as `typealias` output, decomposition of extended ioctl ranges, conditional rendering for booleans/tunables, canonical network context ordering, and conversion of InfiniBand hex ranges to decimal in the expected output.
