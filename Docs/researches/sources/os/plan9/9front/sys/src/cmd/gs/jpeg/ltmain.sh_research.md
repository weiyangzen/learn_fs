# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/ltmain.sh

Purpose: GNU libtool 1.2 runtime script fragment appended by `ltconfig` to implement generalized compile, link, install, execute, finish, and uninstall operations.

Key contents:
- Validates `LTCONFIG_VERSION` against `VERSION`.
- Parses common options such as `--mode`, `--dry-run`, `--features`, `--finish`, `--silent`, `--version`, and `-dlopen`.
- Infers mode from the command when `--mode` is not supplied.
- `compile` mode builds `.lo` libtool objects and optional `.o` old-style objects, using PIC flags when shared libraries are enabled.
- `link` mode handles ordinary objects, `.lo`, `.la`, `-L`, `-l`, `-rpath`, `-version-info`, `-release`, `-static`, `-all-static`, `-dlopen`, `-dlpreopen`, and `-export-dynamic`.
- Creates shared libraries, static archives, reloadable objects, executable wrappers, `.la` metadata files, and symlinks as needed.
- `install` mode installs `.la`, `.a`, `.lo`, and wrapped executables, relinking when the configured platform requires it.
- `finish` mode runs post-install shared-library cache/path commands and prints runtime-linking guidance.
- `execute` mode adjusts shared-library path variables and runs programs, translating wrapper scripts to real uninstalled binaries.
- `uninstall` mode removes libtool archives and associated shared/static library files.
- Ends with mode-specific help text.

Important behavior:
- The generated `libtool` script depends on variables emitted by `ltconfig`, such as `build_libtool_libs`, `build_old_libs`, `objdir`, `archive_cmds`, `hardcode_action`, and library path variable names.
- Executables linked against uninstalled libtool libraries are wrapped by shell scripts that locate the real binary under the object directory and set the library path.
- `.la` files record dlopen name, library names, static archive name, dependency libraries, version info, and install directory.
- Supports dry-run operation by printing commands without executing them.
- This is build-system infrastructure only; it has no JPEG image-processing logic.

Dependencies:
- Shell, compiler/linker/archive commands configured by `ltconfig`, `sed`, `egrep`, `sort`, `uniq`, `nm`, install/copy/remove tools.
