<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/CMakeLists.txt -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/CMakeLists.txt

Purpose: declares FSAL API latency and correctness test binaries.

Important build surface: each test source is assigned to a small source variable, built with `add_executable`, passed through `add_sanitizers`, linked to `ganesha_nfsd`, `${LIBTIRPC_LIBRARIES}`, `${UNITTEST_LIBS}`, `${LTTNG_LIBRARIES}`, `${LTTNG_CTL_LIBRARIES}`, and `${GPERFTOOLS_LIBRARIES}`, and compiled with `${UNITTEST_CXX_FLAGS}`. Covered binaries include lookup, readlink, mkdir, symlink, link, unlink, rename, getattrs, close, commit2, write2, read2, open2, close2, reopen2, setattr2, readdir, mknode, lock_op2, handle_to_key, release, handle_to_wire, and readdir correctness.

Control flow/state: build-only; no `add_test` registrations are present, so CTest will not automatically run these binaries from this file alone.

Dependencies/integration: all binaries depend on the embedded Ganesha test harness and direct FSAL APIs. LTTng and gperftools are linked because many tests expose runtime tracing/profiling CLI flags.

Risks: heavy repetition makes source additions error-prone and easy to forget in one stanza. Linking tracing/profiling libraries for all binaries can complicate minimal environments. Absence of `add_test` reduces CI signal unless another layer invokes binaries.

Test signals: build all declared targets and run selected binaries with `--config`, `--export`, optional `--session`, and optional `--profile` against a prepared export.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/CMakeLists.txt -->
