# sources/test-tools/liburing/configure

## sources/test-tools/liburing/configure

Purpose: POSIX shell configure script that detects compiler/platform/kernel-header capabilities, writes `config-host.mak` and `config-host.h`, supports out-of-source build proxy Makefiles, and generates public compatibility/version headers.

Important functions/APIs: option parser for install dirs, compilers, `--use-libc`, `--enable-sanitizer`, `--enable-tsan`; helpers `fatal`, `print_config`, `do_cc`, `do_cxx`, `compile_prog`, `compile_prog_cxx`, `output_mak`, `output_sym`; generated symbols such as `CONFIG_NOLIBC`, `CONFIG_HAVE_KERNEL_RWF_T`, `CONFIG_HAVE_OPEN_HOW`, `CONFIG_HAVE_STATX`, `CONFIG_HAVE_UCONTEXT`, `CONFIG_HAVE_MEMFD_CREATE`, `CONFIG_HAVE_NVME_URING`, `CONFIG_HAVE_FUTEXV`, `CONFIG_HAVE_UBLK_HEADER`, sanitizer/TSAN flags.

Control flow: parse options and defaults, optionally print help, create out-of-source forwarding Makefiles, prepare temp compile files with cleanup trap, initialize config outputs, run a sequence of compile probes, write feature symbols, emit compiler/build variables, query `Makefile.common` for version, generate `src/include/liburing/io_uring_version.h`, and generate `src/include/liburing/compat.h` with fallback type/constant definitions.

State and persistence: removes and recreates `config-host.mak`, `config-host.h`, `config.log`, generated version and compatibility headers, and out-of-source stub Makefiles. Uses a temp directory cleaned on exit.

Dependencies/integration: invokes C/C++ compilers, `make`, kernel/uapi headers, pkg-config for libbpf, optional clang/bpftool for BPF, and architecture support for nolibc. Its outputs are included by top-level, src, examples, and tests.

Risks: compile probes depend on host headers and cross-compilers being runnable enough for compile/link checks. The script calls `clang -target bpf` even when `clang` may not exist, causing logged shell errors but nonfatal behavior. `--disable-werror` is mentioned in an error message but not parsed. Generated headers are source-tree state and must be cleaned for reproducibility.

Test signals: CI exercises native, cross, sanitizer, TSAN, out-of-source, and musl configure paths. Successful generated config enables all downstream builds.
