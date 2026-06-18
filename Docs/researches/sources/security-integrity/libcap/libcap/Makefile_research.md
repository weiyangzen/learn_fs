## sources/security-integrity/libcap/libcap/Makefile

Purpose: builds libcap and optional libpsx static/shared libraries, generated capability names, pkg-config files, executable shared-object metadata, tests, and install artifacts.

Important targets/variables: `CAPFILES`, `PSXFILES`, `CAPOBJS`, `PSXOBJS`, `cap_names.h`, `cap_names.list.h`, `_makenames`, `libcap.a`, `libpsx.a`, shared `libcap.so*`/`libpsx.so*`, `loader.txt`, `cap_magic.o`, `psx_magic.o`, `cap_test`, `libcapsotest`, `libpsxsotest`, `install-*`, and `clean`.

Control flow: includes `Make.Rules`, forces PIC and libpsx pthread linkage, removes problematic `-Bsymbolic-functions`, generates pkg-config files from templates, extracts capability names from the local UAPI header, optionally creates gperf lookup code, builds static libs, builds shared libs with `__so_start` entry and `.interp` loader data, tests executable shared libs and `cap_test`, and installs headers/libraries/pkg-config metadata.

State/persistence: creates object files, archives, shared libs/symlinks, generated headers, gperf output, loader text, pkg-config files, and install tree files.

Dependencies/integration: C compiler/linker/ar/ranlib/objcopy/sed/egrep, optional gperf, top-level psx sources, libcap headers, and packaging paths.

Risks: generated-name correctness depends on UAPI regex; executable shared-object trick is linker/loader sensitive; install symlink logic must match soname versioning; shared build depends on loader extraction from `empty`.

Test signals: `make -C libcap test`, `./libcap.so --summary`, `./libpsx.so`, `cap_test PASS`, staged install and pkg-config checks.
