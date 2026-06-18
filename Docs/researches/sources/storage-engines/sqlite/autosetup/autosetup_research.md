<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/autosetup/autosetup -->
# sources/storage-engines/sqlite/autosetup/autosetup

## Purpose
This is SQLite's bundled standalone autosetup Tcl script. It is both the autosetup driver and a self-contained module bundle that parses configure options, loads `auto.def`, manages definitions/substitutions, reports help/reference text, installs local/system autosetup copies, and provides portability helpers for Tcl and Jim Tcl.

## Important APIs, Types, And Functions
The top-level `main` proc determines autosetup directories, source directory, build directory, wrapper invocation, option state, dependencies, and command-line definitions. Core option APIs are `options-add`, `options`, `options-defaults`, `opt-bool`, `opt-val`, `opt-str`, and `option-check-names`. Definition APIs are `define`, `undefine`, `define-push`, `define-append`, `define-append-argv`, `get-define`, `is-defined`, `is-define-set`, and `all-defines`. Environment/path/logging APIs include `get-env`, `env-is-set`, `readfile`, `writefile`, `quote-if-needed`, `quote-argv`, `find-executable*`, `configlog`, `msg-checking`, `msg-result`, `msg-quiet`, `user-error`, `autosetup-error`, `relative-path`, `autosetup_add_dep`, `use`, and `autosetup_load_module`.

Embedded modules include formatting backends (`asciidoc-formatting`, `markdown-formatting`, `text-formatting`, `wiki-formatting`, and shared `formatting`), `getopt`, `help`, `init`, `install`, `misc`, and `util`. The install module exposes `autosetup_install`, `autosetup_create_configure`, `autosetup_install_file`, and `autosetup_install_readme`. Utility functions include `compare-versions`, `suffix`, `prefix`, and `lpop`.

## Control Flow
The shell/Tcl polyglot header uses `autosetup-find-tclsh` to exec a working interpreter. `main` initializes `autosetup(libdir)` enough to load `misc`, normalizes script paths, decides whether it was invoked directly or via a `configure` wrapper, initializes option/default/help dictionaries, loads `util` and `getopt`, registers core options, processes early exits (`--version`, `--help`, `--license`, `--reference`, `--install`, `--init`, `--sysinstall`), validates `auto.def`, converts trailing `NAME=VALUE` arguments to definitions, logs invocation details, loads local and auto modules, then sources `auto.def` as a module.

Option declaration is two-phase: `getopt` first captures syntactic options without knowing their validity, then `options-add` registers declared options and maps user-provided values into `autosetup(optset)`. When `auto.def` calls `options`, unknown options are rejected if `option-checking` is enabled. Module loading checks embedded `modsource(...)` first, then external module files under the installed libdir and project `autosetup` directory. The final entrypoint catches errors and formats them through `error-dump` unless debug mode is enabled.

## State And Persistence Behavior
Runtime state is stored in global `autosetup(...)`, `define(...)`, `libmodule(...)`, and `modsource(...)` arrays/dicts. Persistent outputs include `config.log` via `configlog`, files written by configure modules through `writefile`, generated `configure` wrappers from install mode, installed autosetup support files, and project-local `autosetup/README.autosetup`. Dependency state is accumulated in `autosetup(deps)` for generated make/config files to know what should trigger reconfiguration.

## Dependencies And Integration Points
The script depends on a Tcl or Jim Tcl interpreter, the companion `autosetup-find-tclsh`, optional `jimsh0.c` bootstrap support, optional `autosetup-config.guess`/`autosetup-config.sub`, project `auto.def`, external autosetup modules, environment variables, and platform shell utilities such as `chmod`, `uname`, and install-time file operations. SQLite's `configure` wrappers export `WRAPPER`, which changes source-directory discovery. The command surface exposed by this script is what SQLite `auto.def` and teaish extension configs consume.

## Risks
Because it is a configure driver, errors in option parsing, wrapper path normalization, module lookup, or definition quoting can affect all generated build files. `define-append` is not safe for values containing spaces; callers must use `define-append-argv`. The script supports both Tcl and Jim Tcl, so portability helpers in `misc` are sensitive. Install mode can overwrite `configure` when `--force` is used. Error-location logic tries to suppress framework stack traces, which is good for users but can hide details unless `--autosetup-debug` is used.

## Test Signals
Strong signals are `autosetup --version`, `--help`, `--reference` in text/markdown/asciidoc/wiki modes, `--init`, local `--install`, `--sysinstall` from a development tree, successful configure wrapper invocation with `WRAPPER`, unknown-option rejection after `auto.def` declares options, correct `config.log` creation, and module loading from both embedded and project-local module paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/autosetup/autosetup -->
