# sources/test-tools/syzkaller/executor/common_ext_example.h

Purpose: This test-only extension implementation demonstrates how `common_ext.h` hooks are wired into generated executor/csource builds.

Important APIs and types: It defines `SYZ_HAVE_SETUP_EXT`, `setup_ext`, `SYZ_HAVE_SETUP_EXT_TEST`, and `setup_ext_test`. `setup_ext` logs a debug message. `setup_ext_test` writes an eight-byte marker to `SYZ_DATA_OFFSET + 0x1234`.

Control flow and state: When `SYZ_TEST_COMMON_EXT_EXAMPLE` is enabled, `common.h` includes this header instead of the empty extension header. The global setup hook runs during VM/program setup. The test hook runs inside each test process before executing the generated program. The only persistent effect is the marker written into syzkaller’s data area for test verification.

Dependencies and integration points: It depends on `debug`, `memcpy`, and `SYZ_DATA_OFFSET` from the surrounding executor template. It is referenced by tests such as `TestCommonExt` through the marker write noted in the comment.

Risks and test signals: This file is deliberately simple, but it exercises a high-risk extension mechanism. Tests should confirm both hooks are called once at the expected stages, the marker bytes are present in the data mapping, and normal builds do not include this example unless the test macro is set.
