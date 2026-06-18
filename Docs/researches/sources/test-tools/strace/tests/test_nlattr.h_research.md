<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/test_nlattr.h -->
# sources/test-tools/strace/tests/test_nlattr.h

## Purpose
Covers shared strace test helper definitions for `test_nlattr`. Source comments/macros state: len < sizeof(obj_) short read of sizeof(obj_) sizeof(obj_) len < sizeof((obj_)[0]) sizeof((obj_)[0]) < len < sizeof(obj_) short read of sizeof(obj_) %p sizeof(obj_) len < sizeof(obj_) short read of sizeof(obj_) sizeof(obj_) len < sizeof((obj_)[0]) sizeof((obj_)[0]) < len < sizeof(obj_) short read of sizeof(obj_) %p sizeof(obj_) Checks for specific typical decoders %.*f s %.*f s Source read: 526 lines, 17238 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "print_fields.h", <inttypes.h>, <stdio.h>, <stdint.h>, <string.h>, <sys/socket.h>, <unistd.h>, "netlink.h", <linux/rtnetlink.h>; defines/undefs: PRINT_SOCK, TEST_NLATTR_EX_, TEST_NLATTR_, TEST_NLATTR, TEST_NLATTR_OBJECT_EX_, TEST_NLATTR_OBJECT_EX, TEST_NLATTR_OBJECT, TEST_NLATTR_OBJECT_, TEST_NLATTR_OBJECT_MINSZ, TEST_NLATTR_ARRAY_, TEST_NLATTR_ARRAY, TEST_NESTED_NLATTR_, TEST_NESTED_NLATTR_OBJECT_EX_MINSZ_, TEST_NESTED_NLATTR_OBJECT_EX_, TEST_NESTED_NLATTR_OBJECT_EX, TEST_NESTED_NLATTR_OBJECT, TEST_NESTED_NLATTR_ARRAY_EX_, TEST_NESTED_NLATTR_ARRAY_EX, TEST_NESTED_NLATTR_ARRAY, DEF_NLATTR_INTEGER_CHECK_, TEST_NLATTR_VAL; C functions: init_nlattr, print_nlattr, print_sockfd, check_clock_t_nlattr; struct types: nlattr, nlmsghdr; harness commands: check_##nla_data_name_##_nlattr(int fd, void *nlh0, size_t hdrlen, \, check_##type_##_nlattr((fd_), (nlh0_), (hdrlen_), \, check_clock_t_nlattr(int fd, void *nlh0, size_t hdrlen,.

## Control Flow
loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations.

## State And Persistence Behavior
No independent runtime state is owned here; including tests receive compile-time constants, macros, inline helpers, and declarations.

## Dependencies And Integration Points
Depends on `tests.h`, Linux UAPI headers. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: expected output is sensitive to xlat and string-escaping mode. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; signals are compile success and behavior of including tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/test_nlattr.h -->
