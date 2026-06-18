<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/configure.ac -->
# `sources/test-tools/filebench/configure.ac`

Purpose: Autoconf input for Filebench 1.5-alpha3. It discovers compiler tools, platform headers, libc functions, libraries, OS-specific direct I/O/AIO/semaphore features, and emits `Makefile`, `workloads/Makefile`, and `cvars/Makefile`.

Important APIs and macros: `AC_INIT`, `AC_CONFIG_MACRO_DIRS`, `AM_CONFIG_HEADER`, `AM_INIT_AUTOMAKE([subdir-objects])`, `AC_PROG_CC`, `AC_PROG_LIBTOOL`, `AC_PROG_YACC`, `AC_PROG_LEX`, many `AC_CHECK_HEADERS`, `AC_CHECK_FUNCS`, `AC_CHECK_LIB`, `AC_TRY_COMPILE`, `AC_DEFINE`, and `AC_OUTPUT`. It defines feature macros consumed by the C tree, including `HAVE_AIO`, `HAVE_AIOWAITN`, `HAVE_SYSV_SEM`, `HAVE_ROBUST_MUTEX`, `HAVE_PROCSCOPE_PTHREADS`, `HAVE_OFF64_T`, `HAVE_STAT64`, `HAVE_FADVISE`, `HAVE_IOPRIO`, `HAVE_O_DIRECT`, `HAVE_NOCACHE_FCNTL`, and others.

Control flow: the script initializes the package, checks programs, then performs simple header/function checks, specialized type/structure compile probes, library checks, optional `--enable-system`, and final direct-I/O feature detection. Fatal behavior is limited to missing `math.h`.

State and persistence: generated `config.h` and Makefiles persist platform decisions. No runtime state is modified except normal configure-generated cache/output files. It probes `/proc/sys/kernel/shmmax` but only records whether it exists.

Dependencies and integration: integrates Autotools with `sources/test-tools/filebench/cvars/Makefile.am` and workload builds. Links expected libraries include `rt`, `m`, `pthread`, and `dl`; generated macros drive portability branches in the wider Filebench source.

Risks: uses obsolete Autoconf macros such as `AC_TRY_COMPILE`, `AM_CONFIG_HEADER`, and `AC_PROG_LIBTOOL`. Several tests use shell `==`, which is less portable than `=` in `/bin/sh`. Some `AC_CHECK_FUNCS` blocks define the same feature macro once per found function, which can overstate grouped capability unless all call sites also test individual `HAVE_*` macros. Comments note `semtimedop` handling may be incorrect. Duplicate `AC_FUNC_MMAP` is harmless but noisy.

Test signals: successful `autoreconf/configure` should produce `config.h` and the three Makefiles. Regression checks should include Linux and non-Linux configurations for direct I/O, AIO, semaphore, large-file, and pthread feature macros.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/configure.ac -->
