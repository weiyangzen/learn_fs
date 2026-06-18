# sources/test-tools/ltp/testcases/kernel/fs/doio/Makefile

Purpose: builds and installs the LTP `doio` filesystem stress tools and shared helper objects.

Important APIs/types/functions: `top_srcdir`, `testcases.mk`, `CFLAGS`, `LDLIBS`, `MAKE_TARGETS`, `INSTALL_TARGETS`, pattern rule `%.o`, and `generic_leaf_target.mk`.

Control flow: imports LTP testcase build rules, adds large-file support and include path for `doio/include`, links with realtime and pthread libraries, declares executables `growfiles`, `doio`, and `iogen`, installs `rwtest`, and makes each executable depend on shared helper objects such as `dataascii.o`, `databin.o`, `datapid.o`, `bytes_by_prefix.o`, and others.

State/persistence behavior: build outputs are object files and binaries; runtime state belongs to the built tools, not this Makefile.

Dependencies/integration: integrates older SGI-style filesystem stress utilities into LTP. Depends on helper sources and headers under the same doio tree and the LTP generic leaf build system.

Risks/test signals: missing helper objects or include paths break all three tools. Link dependencies on `-lrt -lpthread` are required by async/threaded helpers.
