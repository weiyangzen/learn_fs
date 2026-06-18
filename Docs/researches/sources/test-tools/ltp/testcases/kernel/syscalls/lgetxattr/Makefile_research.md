# sources/test-tools/ltp/testcases/kernel/syscalls/lgetxattr/Makefile

Purpose: builds the `lgetxattr` tests. It includes standard LTP testcase rules and generic leaf targets without additional libraries. Runtime xattr availability is handled in the C files through `HAVE_SYS_XATTR_H` and filesystem support checks. Build state is minimal. Integration risk is platforms without `<sys/xattr.h>`, which compile to TCONF paths rather than functional tests. Test signal is successful build of the xattr test binaries.
