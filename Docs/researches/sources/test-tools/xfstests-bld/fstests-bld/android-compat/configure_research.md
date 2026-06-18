# sources/test-tools/xfstests-bld/fstests-bld/android-compat/configure

Purpose: generated GNU Autoconf 2.69 script that configures the android-compat subpackage and emits `Makefile` from `Makefile.in`.

Important APIs and functions: generated shell helpers for portable echo, path lookup, option parsing, temp directory creation, compile tests, `config.status` generation, and substitutions for `CC`, `CFLAGS`, `RANLIB`, build/host triplets, and installation directories.

Control flow: initializes portable shell environment, parses standard configure options and precious variables, finds `install-sh`/`config.guess`/`config.sub` in `../e2fsprogs-libs/config`, canonicalizes build and host, discovers a C compiler and `ranlib`, checks compiler behavior, registers `Makefile` in `CONFIG_FILES`, writes `config.status`, and runs it unless `--no-create` was given.

State and persistence: writes `config.log`, `config.status`, cache data if requested, and the configured `Makefile`. Temporary `conftest*` and `conf*` files are cleaned on normal exit.

Dependencies and integration: generated from `configure.ac`; invoked by `build-all` before building the Android compatibility library.

Risks: generated script is large and sensitive to missing e2fsprogs config helpers. Environment changes across cached runs cause explicit failure. It should usually be regenerated from `configure.ac` rather than manually edited.

Test signals: successful completion with a valid `Makefile` and compiler/ranlib substitutions.
