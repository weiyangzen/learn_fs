# sources/security-integrity/ima-evm-utils/src/Makefile.am

## Purpose
`src/Makefile.am` is the Automake manifest for building ima-evm-utils' library and command-line tool from the `src` directory. It declares the installed `libimaevm.la` shared library, the `evmctl` binary, generated hash metadata sources, installed public headers, optional feature defines, TPM/TSS backend source selection, and cleanup/dist rules.

## Important APIs, Types, And Functions
The primary Automake targets are `lib_LTLIBRARIES = libimaevm.la`, `bin_PROGRAMS = evmctl`, and `include_HEADERS = imaevm.h`. The library source is `libimaevm.c` plus generated `hash_info.h` and `hash_info.c` listed in `nodist_libimaevm_la_SOURCES`. The binary sources are `evmctl.c` and `utils.c`, with one PCR backend selected from `pcr_tss.c`, `pcr_ibmtss.c`, or `pcr_tsspcrread.c`.

Important build variables include `libimaevm_la_CPPFLAGS`, `libimaevm_la_LDFLAGS`, `libimaevm_la_LIBADD`, `libimaevm_la_CFLAGS`, `evmctl_CPPFLAGS`, `evmctl_LDFLAGS`, `evmctl_LDADD`, `evmctl_CFLAGS`, `AM_CPPFLAGS`, `BUILT_SOURCES`, `EXTRA_DIST`, `CLEANFILES`, and `DISTCLEANFILES`. Conditional Automake blocks consume configuration symbols such as `CONFIG_SIGV1`, `CONFIG_IMA_EVM_ENGINE`, `CONFIG_IMA_EVM_PROVIDER`, `USE_PCRTSS`, and `USE_IBMTSS`.

## Control Flow
Automake translates this manifest into make rules. A normal build first generates `hash_info.h` and `hash_info.c` by running `hash_info.gen` and `hash_info.genc` with `$(KERNEL_HEADERS)`, then compiles `libimaevm.la` with OpenSSL/libcrypto flags and optional feature defines. It then compiles `evmctl` with libcrypto, keyutils, the local library, optional readline flags, and exactly one PCR/TSS source path depending on configured TSS support.

Feature conditionals append preprocessor defines to both the library and `evmctl` so that signature version 1, OpenSSL engine support, and OpenSSL provider support remain consistent between library code and the CLI. TPM conditionals choose Intel TSS, IBM TSS, or command-line PCR reader integration, and the IBM TSS branch also adds `-libmtss`.

## State And Persistence Behavior
The file itself persists no runtime state, but the generated build creates and removes generated sources. `hash_info.h` and `hash_info.c` are build products derived from kernel headers, while `hash_info.gen` and `hash_info.genc` are distributed helper scripts. `CLEANFILES` removes generated hash files and `tmp_hash_info.h`; `DISTCLEANFILES` defers additional cleanup to configure-time substitution. The shared library ABI is controlled through libtool `-version-info 5:0:0`, so changes here influence installed soname/version behavior.

## Dependencies And Integration Points
The build integrates with Autotools conditionals and substitutions produced by `configure.ac` or included m4 macros. External dependencies include OpenSSL/libcrypto through `$(LIBCRYPTO_CFLAGS)` and `$(LIBCRYPTO_LIBS)`, `keyutils` through `-lkeyutils`, optional readline through `$(LDFLAGS_READLINE)`, optional IBM TSS through `-libmtss`, optional Intel TSS source support, and kernel headers through `$(KERNEL_HEADERS)` for generated hash algorithm metadata. `AM_CPPFLAGS = -I$(top_srcdir) -include config.h` makes the project root and generated configuration header visible to all targets in this directory.

`include_HEADERS = imaevm.h` installs the public API header alongside `libimaevm.la`, while `evmctl_LDADD` links the CLI against the just-built library, keeping command behavior aligned with exported library implementation. Distribution integration is explicit: generated outputs are `nodist`, but generator scripts are included in `EXTRA_DIST`.

## Risks And Edge Cases
`BUILT_SOURCES = hash_info.h hash_info.h` lists `hash_info.h` twice and omits `hash_info.c`; if intentional build ordering is expected for `hash_info.c`, this duplicate may be a latent Automake mistake even though `nodist_libimaevm_la_SOURCES` can still force generation. Both generated files depend only on `Makefile`, not the generator scripts or `$(KERNEL_HEADERS)`, so changes to kernel headers or generator scripts may not automatically regenerate outputs unless another dependency path exists. The generator commands use `$(srcdir)/...`, which is good for out-of-tree builds, but generated outputs land in the build directory and must be found correctly by include paths.

The TSS selection is mutually exclusive through nested conditionals, so a configuration with both `USE_PCRTSS` and `USE_IBMTSS` selects Intel TSS and ignores IBM TSS. The IBM link flag spelling `-libmtss` assumes the linker library name and platform conventions are correct. ABI version `5:0:0` requires deliberate maintenance when public library interfaces change; incorrect version-info can break downstream packaging expectations.

## Test Signals
Build-system signals include `autoreconf`/`configure` success across feature combinations, `make V=1` showing expected feature defines, generated `hash_info.h` and `hash_info.c` creation from selected kernel headers, successful `make distcheck`, and clean removal of generated files through `make clean` and `make distclean`. Matrix builds should cover default PCR command backend, `USE_PCRTSS`, `USE_IBMTSS`, `CONFIG_SIGV1`, engine support, provider support, and out-of-tree builds. Runtime smoke tests should confirm `evmctl` links against the local `libimaevm.la` and resolves libcrypto, keyutils, and optional TSS symbols.
