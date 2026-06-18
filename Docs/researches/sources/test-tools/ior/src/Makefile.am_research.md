# sources/test-tools/ior/src/Makefile.am

Purpose: Automake build definition for IOR, mdtest, md-workbench, the shared `libaiori.a`, optional backend AIORI modules, capability-uppercase binaries, and build flag export.

Important targets/variables: `bin_PROGRAMS` builds `ior`, `mdtest`, and `md-workbench`, with uppercase variants under `USE_CAPS`. `noinst_HEADERS` lists internal headers. `libaiori_a_SOURCES` starts with core sources. Each program has source, flags, LDADD, and CPPFLAGS variables. Conditional blocks append backend sources and libraries for HDFS, CUDA/GPU Direct, HDF5, IME, MPIIO, NCMPI, MMAP, POSIX, AIO, PMDK, RADOS, CEPHFS, LIBNFS, DAOS, GFARM, CHFS, FINCHFS, S3 variants, and Lustre. Uppercase program variables mirror lowercase ones. `all-local: build.conf` writes effective LDFLAGS and CFLAGS. `.cu.o` compiles CUDA sources with `NVCC`.

Control flow/state: automake conditionals select optional modules at configure time, then shared `extra*` variables are appended to all main programs and the static library. `build.conf` is regenerated during local build.

Dependencies/integration: tied to autotools conditionals from configure scripts and external storage/HPC libraries. GPU Direct adds C++ linkage through `-lstdc++`.

Risks/test signals: optional backend flags can leak into all programs and duplicate sources in both program and library lists. Hard-coded HDFS paths are brittle. Build tests should exercise minimal POSIX, MPI, CUDA/GPU, and several optional backend configure combinations, plus distcheck for generated `build.conf`.
