<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/Makefile -->
## sources/test-tools/liburing/test/Makefile

Purpose: builds the liburing test suite and declares the sorted list of C/C++ test sources, including every test in this subset.

Important APIs/types/functions: variables define root, install prefix, clang/bpftool locations, BPF output paths, CPPFLAGS, CFLAGS/CXXFLAGS, sanitizer/TSAN additions, and LDFLAGS linking against `../src/liburing` and pthreads. `test_srcs` is the central sorted manifest of test programs.

Control flow: make includes `../config-host.mak` except for clean, appends include paths and generated config header, sets `LIBURING_BUILD_TEST`, applies warning suppressions based on config probes, and links tests with liburing. Later rules outside the shown prefix build binaries, BPF objects, install, and clean artifacts.

State and persistence behavior: build outputs are generated under the test/build output tree and BPF output directory. The makefile itself is declarative and does not persist runtime test state.

Dependencies and integration points: depends on configured liburing source tree, generated `config-host.h`, `config-host.mak`, clang/bpftool for BPF tests, pthreads, and the full test source manifest.

Risks: the sorted manifest is easy to accidentally desynchronize when adding tests. Sanitizer and TSAN flags change execution behavior; syzkaller reproducers often skip under sanitizer. Missing bpftool/clang affects BPF-specific tests but should not break unrelated builds.

Test signals: successful make confirms headers and library objects compile against all listed regression tests; individual test execution supplies behavioral coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/Makefile -->
