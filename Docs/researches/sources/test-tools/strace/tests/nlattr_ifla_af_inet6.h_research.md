# sources/test-tools/strace/tests/nlattr_ifla_af_inet6.h

Purpose: shared helper header for nested `IFLA_AF_SPEC`/IPv6 interface-link attribute tests.

Important APIs, types, and helpers: IPv6 link attribute constants such as `IFLA_INET6_*`, nested nlattr macros including `TEST_NESTED_NLATTR_OBJECT_EX_` and `TEST_NESTED_NLATTR_ARRAY_EX_`, IPv6 cache/config/stats structures, and caller-provided `init_msg`/`print_msg` callbacks.

Control flow: defines static helper functions that build nested IPv6 AF_SPEC attribute payloads and arrays, covering flags, cacheinfo, conf arrays, stats arrays, token/address generation mode, and unknown/truncated nested objects. Including tests invoke these helpers from their own `main`.

State and persistence: no runtime persistence; all state is synthetic nested attribute memory provided to strace through sendto.

Dependencies and integration points: depends on Linux `if_link.h` IPv6 attribute definitions and the strace nlattr test macro framework. It is integrated into interface-info nlattr coverage.

Risks and edge cases: nested array length alignment, evolving IPv6 per-interface attribute constants, and object-size changes are the main maintenance risks.

Test signals: not a standalone test. Including tests should emit decoded nested IPv6 AF_SPEC attributes with structured object/array formatting and appropriate fallback on malformed payloads.
