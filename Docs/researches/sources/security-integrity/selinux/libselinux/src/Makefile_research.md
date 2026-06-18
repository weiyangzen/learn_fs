# sources/security-integrity/selinux/libselinux/src/Makefile

Purpose: This makefile builds the libselinux C library, static archive, shared object, pkg-config file, and Python/Ruby language bindings. It discovers Python and Ruby build metadata through `python -m sysconfig`, `importlib.machinery`, `pkg-config`, and `RbConfig`, then compiles all non-generated C sources except `audit2why.c` into `libselinux.a` and `libselinux.so.1`.

Important targets and variables: `all`, `pywrap`, `rubywrap`, `install`, `install-pywrap`, `install-rubywrap`, `clean`, and `distclean` are the primary control points. `SRCS`, `OBJS`, and `LOBJS` select C inputs; `DISABLE_X11`, `DISABLE_SHARED`, `ANDROID_HOST`, and `LABEL_BACKEND_ANDROID` change backend coverage. `LD_SONAME_FLAGS` applies soname, version-script, `-z defs`, and RELRO flags on ELF builds. Feature probes add `HAVE_STRLCPY` and `HAVE_REALLOCARRAY`.

Control flow: variable setup detects toolchain, Python/Ruby ABI suffixes, warning flags, and optional backend source filtering. Build targets generate SWIG wrappers, compile PIC and non-PIC objects, link the archive/shared library, generate `libselinux.pc`, and install artifacts into `DESTDIR`-qualified library/include/runtime paths.

State and persistence: persistent outputs are `libselinux.a`, `libselinux.so.1`, `libselinux.so`, generated SWIG files, wheel contents, Ruby extension, and `libselinux.pc`. It never mutates runtime SELinux state.

Dependencies and integration: depends on compiler, archive tools, `pkg-config`, Python, Ruby, SWIG, PCRE flags, libsepol, FTS, `dl`, and public headers under `../include`. It integrates with downstream packagers through install paths and pkg-config substitution.

Risks and test signals: the broad `-Werror` profile makes compiler drift visible. Backend filtering must stay aligned with actual source availability. Install rules should be tested with `DESTDIR`, shared/static toggles, Python/Ruby wrapper builds, Android host mode, and Darwin linker behavior.
