<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpriority/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setpriority/Makefile

Purpose: build glue for the LTP `setpriority` syscall tests. It inherits the common LTP testcase make rules from `include/mk/testcases.mk` and usually delegates target discovery and build recipes to `generic_leaf_target.mk`.

Important APIs/types/functions: this is GNU make metadata rather than C code. Key variables include `top_srcdir`, optional `CPPFLAGS`, `CFLAGS`, `LDLIBS`, `LTPLDLIBS`, `MAKE_TARGETS`, and filtering variables such as `FILTER_OUT_MAKE_TARGETS` when present.

Control flow: make evaluates the local variables, includes the shared LTP testcase rules, then the generic leaf target emits binaries for the C sources in the directory or for explicitly named targets.

State and persistence behavior: no runtime state is created by this file; it controls compile/link state and, where present, dependency selection such as NUMA libraries, pthread flags, compatibility wrappers, or source reuse from sibling directories.

Dependencies and integration points: integrates the `setpriority` directory with the repository-wide LTP build system. Any local flags here are part of the ABI between the test source and the harness, for example selecting compat-16 wrappers, linking libnuma helpers, or building sethostname binaries from setdomainname source.

Risks: changes can silently drop tests, fail cross-architecture builds, or link tests without required helper libraries. Makefiles that reuse another directory source are especially sensitive to preprocessor defines and output target names.

Test signals: successful `make` in the syscall directory produces the expected LTP test binaries; failures show as missing targets, compile errors, link errors, or filtered tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpriority/Makefile -->
