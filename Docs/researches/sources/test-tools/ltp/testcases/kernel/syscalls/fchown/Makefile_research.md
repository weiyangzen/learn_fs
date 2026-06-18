# sources/test-tools/ltp/testcases/kernel/syscalls/fchown/Makefile

Purpose: builds the `fchown` syscall tests and enables compatibility support for 16-bit uid/gid variants.

Important APIs/types/functions: `testcases.mk`, `../utils/compat_16.mk`, and `generic_leaf_target.mk`.

Control flow: includes common testcase rules, then the compatibility make fragment before the generic leaf target.

State/persistence behavior: no runtime state. Build configuration may produce compatibility variants depending on the LTP framework.

Dependencies/integration: local tests include `compat_tst_16.h`; this Makefile connects those wrappers to the build.

Risks/test signals: build failures are likely from missing compatibility support or include path issues.
