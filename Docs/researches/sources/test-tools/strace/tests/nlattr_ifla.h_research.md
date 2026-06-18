# sources/test-tools/strace/tests/nlattr_ifla.h

Purpose: shared helper header for interface-link nlattr tests, factoring common `ifinfomsg` header initialization/printing and reusable attribute checks.

Important APIs, types, and helpers: `struct ifinfomsg`, `hdrlen`, `init_ifinfomsg`, `print_ifinfomsg`, `ifindex_lo`, `PRINT_FIELD_*`, and `test_nlattr.h` macros used by including C files.

Control flow: as a header, it defines static helper functions rather than a `main`. Including tests call these helpers to initialize the netlink header and print a consistent ifinfo prefix before testing attributes.

State and persistence: no persistent state. It provides compile-time shared code and uses only caller-provided message buffers.

Dependencies and integration points: depends on Linux interface/rtnetlink headers and is integrated into route `IFLA_*` nlattr tests, especially `nlattr_ifinfomsg.c` and related files.

Risks and edge cases: because functions are `static` in a header, every includer gets its own copy; signature or expected-output changes must stay aligned with all callers.

Test signals: not executable alone. Its correctness is observed through including tests whose expected output starts with the shared `ifinfomsg` prefix.
