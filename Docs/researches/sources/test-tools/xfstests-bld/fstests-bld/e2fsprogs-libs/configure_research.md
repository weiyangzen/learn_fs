# Research: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/configure

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-009524`: lines 1-9179, `Docs/researches/chunks/subset-b-009524_research.md`
- `subset-b-009525`: lines 9180-12421, `Docs/researches/chunks/subset-b-009525_research.md`

## Chunk Research

### subset-b-009524: lines 1-9179

# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/configure lines 1-9179

## Purpose

This chunk is the first 9,179 lines of a GNU Autoconf 2.65 generated `configure` script for the e2fsprogs library tree embedded under `xfstests-bld`. Its job is to normalize the shell environment, parse user configure options, discover the source/build/host environment, probe the C compiler and platform features, select e2fsprogs library/program build modes, and populate `confdefs.h`, `config.log`, cache variables, and substitution variables that later `config.status` uses to generate build files.

The chunk starts at script bootstrap and ends inside the gettext/NLS setup after assigning `INTLLIBS="$LIBINTL"`. The actual `config.status` generation and later e2fsprogs-specific checks continue after this chunk.

## High-Level Structure

- Lines 1-535: Autoconf/M4sh bootstrap. The script establishes POSIX-ish shell behavior, finds a better shell when required, sanitizes environment variables, defines portable helpers, determines `as_me`, initializes echo/link/mkdir/test helpers, and opens descriptors used for status output.
- Lines 538-826: package and configure metadata. It initializes package identity, default includes, output substitution variables, file substitution variables, supported `--enable`/`--with` options, and precious environment variables.
- Lines 829-1564: command-line parser and help/version handling. It accepts GNU directory options, build/host/target aliases, e2fsprogs feature switches, package switches, `VAR=VALUE` assignments, and source directory resolution.
- Lines 1570-2244: reusable C probe functions. These helpers compile, link, preprocess, run, and check headers/types/functions/members/declarations for later cached tests.
- Lines 2245-2587: `config.log`, site/cache loading, and cache consistency checks. It records platform details, command-line arguments, output variables, file substitutions, and validates that precious variables did not change across cached runs.
- Lines 2591-4288: main body initialization, e2fsprogs version extraction, canonical build/host resolution, C compiler selection, C compiler sanity, GNU C and C89 detection, and C preprocessor discovery.
- Lines 4295-4556: core text/tool/header probes. It finds usable `grep`/`egrep`, checks ANSI headers and default system headers, and determines whether Linux headers are available.
- Lines 4567-5557: e2fsprogs build-policy options. It sets compiler flags, library extensions, root prefix behavior, maintainer/symlink/verbose flags, htree/compression/debug options, shared/profile/checker library modes, private/external uuid and blkid selection, optional programs, TLS, uuidd, and library makefile path variables.
- Lines 5559-6004: package identity override for gettext tooling plus make/install/NLS tool discovery. It sets `PACKAGE=e2fsprogs`, then `VERSION=0.14.1` for gettext macro compatibility, probes make/install helpers, initializes `MKINSTALLDIRS`, and searches gettext tools (`msgfmt`, `gmsgfmt`, `xgettext`, `msgmerge`).
- Lines 6007-7545: archive/runtime/compiler portability probes. It finds `ranlib`, checks `-lcposix`, C keywords/types, integer/printf/alloca/mmap/glibc behavior, inttypes/stdint details, computes `SIZE_MAX` if needed, locates linker `ld`, detects GNU ld, and runs `config.rpath`.
- Lines 7554-9179: libiconv and gettext library resolution. It honors `--with-libiconv-prefix`, resolves iconv library/include/rpath flags, checks `iconv()` and its declaration, probes locale/code-set support and bison, evaluates NLS/gettext choices, searches libc or external `libintl`, falls back to included gettext when needed, and sets NLS-related substitution variables.

## Important Functions and Probe APIs

- `as_fn_unset`, `as_fn_set_status`, `as_fn_exit`, `as_fn_mkdir_p`, `as_fn_append`, `as_fn_arith`, `as_fn_error`: Autoconf shell support functions used throughout the script for portable cleanup, error handling, arithmetic, appending, directory creation, and exits.
- `ac_fn_c_try_compile`, `ac_fn_c_try_link`, `ac_fn_c_try_cpp`, `ac_fn_c_try_run`: central test runners. They create `conftest.*`, execute compiler/preprocessor/link/run commands, write diagnostics into `config.log` on fd 5, clean temporary artifacts, and return success via shell status.
- `ac_fn_c_check_header_mongrel` and `ac_fn_c_check_header_compile`: header checks. The "mongrel" variant compares compiler and preprocessor results and warns when they disagree.
- `ac_fn_c_check_type`, `ac_fn_c_check_func`, `ac_fn_c_compute_int`, `ac_fn_c_check_member`, `ac_fn_c_check_decl`: generic type/function/integer/member/declaration checks. Later code uses these to define `HAVE_*`, replacement type macros, and cache variables.

These are generated shell functions rather than project-authored APIs, but they define the execution model for all subsequent platform detection.

## Important Variables and Build Surface

- `ac_subst_vars` and `ac_subst_files` are the contract with generated make/config files. This chunk registers variables such as `LIBUUID`, `LIBBLKID`, `DEBUGFS_CMT`, `FSCK_PROG`, `USE_NLS`, `LIBINTL`, `LIBICONV`, `E2FSPROGS_VERSION`, `root_prefix`, `MAKEFILE_ELF`, and `PUBLIC_CONFIG_HEADER`.
- `ac_user_opts` defines the accepted public configure switches. e2fsprogs-specific switches include `--enable-elf-shlibs`, `--enable-bsd-shlibs`, `--enable-profile`, `--enable-checker`, `--enable-libuuid`, `--enable-libblkid`, `--enable-debugfs`, `--enable-resizer`, `--enable-fsck`, `--enable-tls`, `--enable-uuidd`, and `--enable-nls`.
- `confdefs.h` accumulates compile-time defines such as `STDC_HEADERS`, `HAVE_*` headers/functions, `ENABLE_HTREE`, `CONFIG_TESTIO_DEBUG`, `CONFIG_BUILD_FINDFS`, `TLS`, `USE_UUIDD`, `HAVE_ICONV`, `ENABLE_NLS`, `HAVE_GETTEXT`, and `HAVE_DCGETTEXT`.
- `config.log` is the persistent diagnostic log for configure probes. It captures platform info, PATH entries, compiler stderr, failed programs, cached values, output variables, file substitutions, and `confdefs.h`.
- `config.cache` is optional and defaults to disabled (`/dev/null`). When enabled, the script validates precious variables (`CC`, `CFLAGS`, `LDFLAGS`, `LIBS`, `CPPFLAGS`, `CPP`, `PKG_CONFIG`, aliases) against prior cached values.

## Control Flow

1. Bootstrap normalizes shell behavior, echo behavior, path separators, stdin/stdout descriptors, and temporary-file cleanup.
2. Argument parsing maps supported options into shell variables and records unknown options for warnings or fatal errors depending on `--enable-option-checking`.
3. Source discovery locates `version.h` as `ac_unique_file`; failure to find it aborts configure.
4. `config.log` is opened and a trap is installed so exits and interrupts write cache/output summaries and remove `conftest*`, `confdefs*`, and configured cleanup files.
5. The main script extracts `E2FSPROGS_VERSION` and release date from `version.h`, canonicalizes build and host triplets via `config.guess`/`config.sub`, and sets `build_cpu/vendor/os` and `host_cpu/vendor/os`.
6. Compiler discovery chooses prefixed tools first for cross builds, then `gcc`, `cc`, and `cl.exe`, rejecting unusable compilers and warning when unprefixed tools are used during cross-compilation.
7. Compile/link/preprocess sanity checks establish `EXEEXT`, `OBJEXT`, `GCC`, default `CFLAGS`, C89 mode, and `CPP`.
8. System header and tool checks define the baseline compilation environment and decide whether bundled Linux headers must be included.
9. e2fsprogs feature switches set comment variables, library names, makefile fragment paths, and compile-time defines that control which libraries/programs get built.
10. gettext/libiconv support probes resolve host tools, library paths, rpath flags, and fallback paths for included gettext.

## State and Persistence Behavior

- Persistent generated outputs in this chunk are `config.log`, `confdefs.h`, optional `config.cache`, temporary `conftest.*` files, and temporary helper files such as `conftest.make`, `conftest.mmap`, and `conftest.txt`.
- The script mutates many shell globals (`LIBS`, `CPPFLAGS`, `LDFLAGS`, `CC`, `CFLAGS`, `LIBINTL`, `LIBICONV`) during probes, generally saving/restoring when a probe should not leak flags. Link checks temporarily prepend candidate libraries.
- Cache variables named `ac_cv_*`, `gt_cv_*`, `am_cv_*`, `jm_ac_cv_*`, and `bh_cv_*` persist probe results when caching is enabled. These cached answers can bypass later compile/run checks.
- `confdefs.h` is append-only within the configure run. Once a feature is detected or enabled, this chunk appends the relevant `#define`.
- Comment variables like `ELF_CMT`, `BSDLIB_CMT`, `PROFILE_CMT`, `CHECKER_CMT`, `DEBUGFS_CMT`, `UUID_CMT`, `BLKID_CMT`, and `UUIDD_CMT` are build-file gates; empty means enabled and `#` means commented out.

## Dependencies and Integration Points

- Requires standard shell tools and Autoconf auxiliary scripts: `config/install-sh` or equivalent, `config/config.guess`, `config/config.sub`, and later `config/config.rpath`.
- Reads `${srcdir}/version.h` for e2fsprogs version/date metadata.
- Integrates with C toolchain and linker discovery through `CC`, `CPP`, `LD`, `RANLIB`, `CFLAGS`, `CPPFLAGS`, `LDFLAGS`, and `LIBS`.
- Uses `pkg-config` when the user disables private `libuuid` or `libblkid`; it requires at least pkg-config 0.9.0 and uses `pkg-config --libs`/`--static --libs`.
- Resolves shared library fragments under `${srcdir}/lib/Makefile.elf-lib`, `Makefile.solaris-lib`, `Makefile.bsd-lib`, `Makefile.darwin-lib`, `Makefile.profile`, `Makefile.checker`, and `Makefile.library`.
- NLS integration depends on gettext tools (`msgfmt`, `gmsgfmt`, `xgettext`, `msgmerge`), optional bison, iconv/libiconv, libintl/gettext, locale headers, and `po`/`intl` build directories.

## Risks and Edge Cases

- This is generated code; direct manual edits are fragile because regeneration from `configure.ac` and macro inputs can overwrite changes.
- Cross-compilation can force guesses or conservative failures for run-time tests (`mmap`, stack direction, POSIX printf, divide-by-zero signal behavior). Cached answers may be needed for unusual targets.
- `VERSION` is deliberately reset from `E2FSPROGS_VERSION` to `0.14.1` before gettext macros emit `PACKAGE`/`VERSION` defines. This is surprising and may confuse consumers expecting package version consistency.
- Disabling private `libuuid`/`libblkid` requires working `pkg-config` and linkable external libraries; otherwise configure aborts.
- `--with-diet-libc` rewrites `CC` to `diet cc -nostdinc` and disables TLS by default, which can interact badly with later compiler and header checks.
- The linker/rpath logic sources `.la` files and executes `config.rpath` output. It assumes these build-tree/support files are trusted.
- `USE_NLS=yes` can still become `no` if neither preinstalled nor included gettext is usable. Conversely, included gettext changes `LIBINTL` to `${top_builddir}/intl/libintl.a` and removes `-lintl` from `LIBS`.
- Header checks intentionally warn and proceed when preprocessor and compiler disagree; downstream code may compile with the compiler result even when preprocessing looked broken.

## Test Signals

- Successful configure output includes version/date messages, build/host triplets, compiler/preprocessor results, feature enable/disable messages, and NLS/gettext source messages.
- `config.log` is the primary debugging artifact for failed probes; failed C programs are printed there with `| ` prefixes.
- Key positive signals include generated defines in `confdefs.h`: `STDC_HEADERS`, `ENABLE_HTREE`, `CONFIG_TESTIO_DEBUG`, `CONFIG_BUILD_FINDFS`, `USE_UUIDD`, `HAVE_ICONV`, `ENABLE_NLS`, `HAVE_GETTEXT`, and `HAVE_DCGETTEXT`.
- Key negative/abort signals include missing `version.h`, missing auxiliary scripts, no acceptable C compiler, failing C preprocessor sanity, missing external uuid/blkid when private libraries are disabled, no acceptable `ld`, and cache corruption from changed precious variables.
- Feature-specific assertions can be tested by running configure with switches such as `--disable-libuuid`, `--disable-libblkid`, `--enable-elf-shlibs`, `--enable-bsd-shlibs`, `--disable-nls`, `--with-libiconv-prefix=DIR`, and inspecting `config.log`, `confdefs.h`, and substituted `MCONFIG`/makefile values after the full script completes.

### subset-b-009525: lines 9180-12421

# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/configure lines 9180-12421

## Scope

This chunk is the final third of the generated GNU Autoconf `configure` script for the bundled `e2fsprogs-libs` copy under `xfstests-bld`. It begins after earlier compiler and option setup and covers build-tool discovery, header/type/function probes, platform-specific installation defaults, generated header creation, cache persistence, and `config.status` generation/execution.

The file is generated shell, not hand-written application logic. The important behavior is the sequence of probes and side effects that produce `confdefs.h`, `public_config.h`, `asm_types.h`, `MCONFIG`, Makefiles, pkg-config files, gettext files, and other configured build artifacts for the e2fsprogs libraries.

## Purpose

The chunk adapts the e2fsprogs library build to the local host and build environment. It answers questions that downstream C and Makefile code depend on:

- Which build utilities are available: `make`, GNU make, `ln`, `mv`, `cp`, `rm`, `chmod`, `awk`, `egrep`, `sed`, `perl`, `ldconfig`, `ar`, `ranlib`, `strip`, and `makeinfo`.
- Which compiler should build host-side helper tools when cross-compiling.
- Which C headers, types, struct members, declarations, functions, libraries, byte order, and integer sizes exist.
- Which platform defaults should apply for Linux, GNU/kFreeBSD-like systems, Cygwin, Solaris, and Darwin.
- Which generated files should be instantiated from templates by `config.status`.

For the larger `xfstests-bld` integration, this script is a bootstrap boundary: successful configuration determines whether the bundled e2fsprogs libraries can be built consistently for the intended test environment.

## Important APIs, Functions, And Variables

The "APIs" in this chunk are Autoconf shell conventions and generated helper functions:

- `ac_fn_c_check_header_mongrel`, `ac_fn_c_check_header_compile`, `ac_fn_c_check_func`, `ac_fn_c_check_member`, `ac_fn_c_check_type`, `ac_fn_c_check_decl`, `ac_fn_c_compute_int`, `ac_fn_c_try_compile`, `ac_fn_c_try_link`, and `ac_fn_c_try_run` are generated probe helpers defined earlier in the script. This chunk uses them heavily to compile, link, or run temporary C programs.
- `confdefs.h` is the accumulating preprocessor-definition file. This chunk appends `HAVE_*`, `SIZEOF_*`, `WORDS_BIGENDIAN`, `AC_APPLE_UNIVERSAL_BUILD`, `_INTL_REDIRECT_MACROS`, and related definitions.
- `config.log` receives probe status, command lines, warnings, and error context through file descriptor 5.
- `config.status` is generated near the end and becomes the durable re-instantiation script for configured files.
- `ac_cv_*` and package-specific `e2fsprogs_cv_*` variables cache probe results. Examples include `ac_cv_prog_make_*_set`, `ac_cv_path_LN`, `ac_cv_prog_AR`, `ac_cv_sizeof_long_long`, `ac_cv_c_bigendian`, `e2fsprogs_cv_struct_st_flags`, and `ac_cv_e2fsprogs_use_static`.
- Substitution variables set here include `SET_MAKE`, `ifGNUmake`, `ifNotGNUmake`, `LN`, `LN_S`, `MV`, `CP`, `RM`, `CHMOD`, `AWK`, `EGREP`, `SED`, `PERL`, `LDCONFIG`, `AR`, `RANLIB`, `STRIP`, `MAKEINFO`, `BUILD_CC`, `ASM_TYPES_HEADER`, `PUBLIC_CONFIG_HEADER`, `SOCKET_LIB`, `SEM_INIT_LIB`, `UNI_DIFF_OPTS`, `LINUX_CMT`, `CYGWIN_CMT`, `UNIX_CMT`, `root_prefix`, root installation directories, `LDFLAG_STATIC`, `SS_DIR`, `ET_DIR`, `DO_TEST_SUITE`, `INTL_FLAGS`, `BUILD_CFLAGS`, and `BUILD_LDFLAGS`.

The generated `config.status` script defines its own portable shell helpers, including `as_fn_error`, `as_fn_set_status`, `as_fn_exit`, `as_fn_unset`, `as_fn_append`, `as_fn_arith`, and `as_fn_mkdir_p`. These are used to parse `config.status` arguments, create directories, substitute `@VAR@` placeholders, and instantiate files.

## Control Flow

The chunk proceeds in a mostly linear Autoconf sequence:

1. It checks whether `${MAKE-make}` sets `$(MAKE)` and sets `SET_MAKE` only when recursive make invocations need an explicit assignment.
2. It searches for GNU make by trying `$MAKE`, `make`, `gmake`, and `gnumake`, then exposes makefile comment variables `ifGNUmake` and `ifNotGNUmake`.
3. It discovers standard file and text-processing tools, using user-provided environment overrides when present and falling back to safe defaults such as `ln`, `mv`, `cp`, `rm`, `:`, or `sed`.
4. It detects archiving and binary tools with cross-prefix preference. For `AR`, `RANLIB`, and `STRIP`, it first tries `${ac_tool_prefix}<tool>` and then unprefixed tools, warning if cross-compiling with an unprefixed fallback.
5. It configures documentation generation through `MAKEINFO`, replacing a missing tool with an echo-and-true command so info docs are skipped instead of failing the whole build.
6. It chooses `BUILD_CC`. Native builds reuse `CC`; cross builds search for a native `gcc` or `cc`.
7. It probes a large set of system headers, then specialized headers requiring prerequisite includes, such as `sys/disk.h`, `sys/mount.h`, and `net/if.h`.
8. It probes functions, declarations, members, and sizes: `vprintf`/`_doprnt`, `struct dirent.d_reclen`, `ssize_t`, `llseek`, `lseek64`, `sizeof(short/int/long/long long)`, and byte order.
9. It runs `$ac_aux_dir/parse-types.sh` with `BUILD_CC` and `CPP` to generate assembly-visible type information, then writes `public_config.h` with the public `HAVE_SYS_TYPES_H` and `WORDS_BIGENDIAN` subset needed by `ext2fs.h`.
10. It probes additional C portability features: `inttypes.h`, `intptr_t`, `struct stat.st_flags`, `UF_IMMUTABLE`, `struct sockaddr.sa_len`, optional `blkid_probe_all`, a broad function list, `-lsocket`, `optreset`, and `sem_init` in libc, `-lpthread`, `-lrt`, or `-lposix4`.
11. It computes host-specific makefile comments and install defaults. Linux-like hosts get `HAVE_EXT2_IOCTLS`, usually default `root_prefix=""`, and default `prefix="/usr"` with `/usr/share/man`; Cygwin flips `UNIX_CMT`; Solaris disables static-linking even if the linker accepts `-static`; Darwin defines `_INTL_REDIRECT_MACROS`.
12. It derives static-link flags, source directory paths for `lib/ss` and `lib/et`, test-suite enablement, intl include flags, and native build flags.
13. It creates required build directories and builds `outlist` by checking whether each source-side template directory exists. The resulting list is appended to `ac_config_files`.
14. It writes `confcache`, updates the configured cache file if writable and changed, computes `DEFS` from `confdefs.h`, expands `LIBOBJS`/`LTLIBOBJS`, and emits the full `config.status` script.
15. Unless `--no-create` was requested, it closes/reopens logging around executing `$SHELL ./config.status`, then warns about unrecognized configure options and makes `util/gen-tarball` executable if generated.

## State And Persistence Behavior

This chunk has many filesystem side effects:

- Temporary C sources, objects, executables, makefiles, awk scripts, and cache fragments are created as `conftest*`, `conf$$*`, or under a temporary `./confXXXXXX` directory and usually removed after each probe.
- `confdefs.h` is appended throughout and later transformed into the `DEFS` substitution string.
- `asm_types.h` is generated indirectly by `parse-types.sh`, and `ASM_TYPES_HEADER=./asm_types.h` is exported for substitutions.
- `public_config.h` is rewritten with only public header-relevant defines for `HAVE_SYS_TYPES_H` and `WORDS_BIGENDIAN`.
- `lib`, `include`, `include/linux`, and `include/asm` directories are created if absent.
- The configure cache file is updated from `confcache` when writable and different.
- `config.status` is created, made executable, and later run to instantiate configured files from `*.in` templates.
- `config.status` writes configured files atomically through a temporary output and `mv`, and it creates output directories as needed.
- Gettext-related `default-1` commands create `POTFILES` and specialized `po/Makefile` content from `POTFILES.in`, `LINGUAS`, and `Makevars` when those inputs exist.

No long-lived application state or daemon state is involved. Persistence is build-tree state: generated headers, makefiles, pkg-config files, caches, and logs.

## Dependencies And Integration Points

The chunk depends on a POSIX-like shell environment plus common build tools. It integrates with:

- The C compiler and linker through compile, link, and run probes.
- Host and target toolchains through `CC`, `BUILD_CC`, `ac_tool_prefix`, `AR`, `RANLIB`, and `STRIP`.
- Shell utilities including `grep`, `egrep` or `$GREP -E`, `sed`, `awk`, `diff`, `mkdir`, `chmod`, `ln`, `cp`, `mv`, `rm`, and optionally `perl`, `ldconfig`, and `makeinfo`.
- e2fsprogs auxiliary script `$ac_aux_dir/parse-types.sh`.
- Optional system libraries: `libblkid`, `libsocket`, `libpthread`, `librt`, and `libposix4`.
- Template-driven build files such as `MCONFIG`, top-level and subdirectory `Makefile`s, library type headers, pkg-config files for `ss`, `uuid`, `com_err`, `e2p`, `blkid`, and `ext2fs`, `e2fsprogs.spec`, `util/subst.conf`, `util/gen-tarball`, and gettext inputs.
- Public e2fsprogs headers, especially `lib/ext2fs/ext2_types.h`, `lib/uuid/uuid_types.h`, `lib/blkid/blkid_types.h`, and `public_config.h`.

This chunk also bridges configure-time results into later make execution. Makefile conditionals consume comment variables such as `LINUX_CMT`, `CYGWIN_CMT`, `UNIX_CMT`, `ifGNUmake`, and `ifNotGNUmake`, while C sources consume `HAVE_*` and `SIZEOF_*` definitions.

## Risks And Edge Cases

- Generated-script fragility: edits to this file can be overwritten by rerunning Autoconf and may diverge from `configure.ac` intent.
- Cross-compilation ambiguity: probes that need execution are avoided or guessed in some cases, but incorrect cached values for byte order, sizes, or declarations can produce incompatible headers.
- Tool fallback masking: missing `makeinfo`, `ranlib`, `strip`, `chmod`, or `ldconfig` may become `:` or an echo command. That keeps configuration moving but can hide incomplete packaging or install behavior.
- Cache poisoning: stale `ac_cv_*` or `e2fsprogs_cv_*` values can bypass real probes and generate incorrect `confdefs.h` and Makefiles.
- Host-specific defaults affect installation paths. Linux-like defaulting of `prefix=/usr`, `root_prefix=""`, and `mandir=/usr/share/man` can surprise callers expecting Autoconf's usual `/usr/local` default.
- The `BLKID_CMT` guard means blkid probing only happens when that earlier variable requests it; consumers must understand whether bundled or system blkid is selected outside this chunk.
- Static-link detection mutates `LDFLAGS` during the probe and then restores it. A failed restoration or hostile environment variable would affect later link tests.
- `sem_init` search order chooses the first successful provider among libc, `-lpthread`, `-lrt`, and `-lposix4`; platform linker behavior can make the selected `SEM_INIT_LIB` important for all downstream targets.
- The generated `config.status` substitution machinery relies on `awk`, delimiter selection, and sed escaping. Values with newlines are explicitly stripped from cache output, so unusual environment values may not round-trip.
- The `net/if.h` prerequisite block tests `#if HAVE_SYS_SOCKET` rather than the more common `HAVE_SYS_SOCKET_H`; if that macro is not defined elsewhere, the compile probe may omit `sys/socket.h` on platforms that require it.

## Test Signals

Useful validation signals for this chunk are configure and build outcomes rather than unit tests:

- Running the generated `configure` script should complete without `as_fn_error`, create `config.status`, update `config.log`, and instantiate the expected `outlist` files.
- `config.log` should show successful or intentionally negative results for required probes, especially C type sizes, endianness, `BUILD_CC`, `sem_init`, static linking, and tool discovery.
- Generated files should exist and be non-empty after configuration: `MCONFIG`, relevant `Makefile`s, `public_config.h`, `asm_types.h`, library type headers, and pkg-config files for enabled libraries.
- A subsequent `make` or package build under `xfstests-bld` exercises whether tool substitutions, root install directories, static flags, gettext outputs, and library dependencies are coherent.
- Cross-build test signals should include checking that host tools are built with `BUILD_CC`, target objects use `CC`, and cached endian/size values match the target ABI.
- On Linux hosts, `confdefs.h` or generated config headers should contain `HAVE_EXT2_IOCTLS`, and install substitutions should reflect `/usr` plus the root-prefix split expected by e2fsprogs.
