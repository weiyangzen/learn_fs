# File Research: sources/os/bsd/dragonflybsd/sys/sys/tbridge.h

DragonFly test bridge ioctl and kernel testcase module interface.

Key contents:
- Defines ioctl commands:
  - `TBRIDGE_LOADTEST`
  - `TBRIDGE_GETRESULT`
- Kernel-only result constants matching `dfregress.h`.
- Defines testcase callback types:
  - abort callback
  - run callback
- Defines `struct tbridge_testcase`.
- Declares:
  - `tbridge_printf`
  - `tbridge_test_done`
  - safe-memory allocation/free/check helpers
  - `tbridge_testcase_modhandler`
- Provides `TBRIDGE_TESTCASE_MODULE` macro for registering testcase modules with dependency on `testbridge`.

Important behavior:
- The result constants must stay synchronized with external regression tooling.
- Safe-memory wrappers capture file/line at allocation/free sites.
- Testcase modules are normal kernel modules with declared dependency/version metadata.

Research notes:
- This is test infrastructure, not production syscall/VFS logic.
- The ABI is small but fragile because it matches out-of-file regression constants.
