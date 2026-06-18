<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/meson.build -->
# Research: sources/user-network-fs/davfs2/meson.build

Purpose: root Meson build definition for davfs2 1.8.0. It configures compile-time constants, dependency checks, subdirectories, optional NLS/man/docs, and install paths.

Important APIs: `project('davfs2','c', version:'1.8.0')`, `_GNU_SOURCE` project argument, OS gate for Linux/FreeBSD, `configuration_data()` for `config.h`, `dependency('neon', required:true)`, `find_library('intl')`, header/function probes, `run_command('po4a','--version', check:true)`, `subdir('src')`, `subdir('etc')`, optional `po` and `man`, and optional `install_data()` for docs.

Control flow and integration: build options from `meson_options.txt` set system/user names, cache/state/cert directories, doc/man/NLS behavior. `config.h` exports path and package constants consumed by C files and man generation. NLS is enabled only when option `nls` is true and `msgfmt` is found.

State and persistence: no runtime state, but it fixes installed paths and default runtime directories into binaries. Documentation install destination is computed from `docdir` or `datadir/doc/davfs2`.

Dependencies: C compiler, Meson >=0.58, neon, po4a, optional gettext/msgfmt/libintl, POSIX/GNU headers and functions. For Meson >=1.3, required functions are asserted.

Risks: `prefix / get_option('datadir')` can double-prefix if `datadir` is already absolute or Meson semantics change; path composition deserves install-tree testing. Requiring po4a at root blocks builds even when man generation is disabled. Function checks are conditional on Meson version, so older Meson may skip required-function enforcement.

Test signals: configure/build on Linux and FreeBSD; `meson configure` option matrix for `man`, `doc`, `nls`; inspect generated `config.h`; run installed binaries against expected default paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/meson.build -->
