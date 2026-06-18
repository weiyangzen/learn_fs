<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/test_netlink.h -->
# sources/test-tools/strace/tests/test_netlink.h

## Purpose
Covers shared strace test helper definitions for `test_netlink`. Source comments/macros state: len < sizeof(obj_) short read of sizeof(obj_) sizeof(obj_) Source read: 104 lines, 3169 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "print_fields.h", <stdio.h>, <stdint.h>, <string.h>, <sys/socket.h>, "netlink.h"; defines/undefs: TEST_NETLINK_, TEST_NETLINK, TEST_NETLINK_OBJECT_EX_, TEST_NETLINK_OBJECT_EX, TEST_NETLINK_OBJECT; struct types: nlmsghdr.

## Control Flow
Straight-line fixture code or helper definitions consumed by other tests.

## State And Persistence Behavior
No independent runtime state is owned here; including tests receive compile-time constants, macros, inline helpers, and declarations.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; signals are compile success and behavior of including tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/test_netlink.h -->
