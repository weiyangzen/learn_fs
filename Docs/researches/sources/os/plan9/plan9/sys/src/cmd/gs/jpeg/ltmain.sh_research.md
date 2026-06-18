# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/ltmain.sh

This is GNU libtool 1.2's main driver body. `ltconfig` appends it to generated configuration variables to form an executable `libtool` script.

The top-level parser handles `--mode`, `--dry-run`, `--features`, `--finish`, `--quiet`, `--version`, `--help`, and `-dlopen`. If no mode is explicit, it infers compile, link, execute, install, or uninstall from the command name and arguments.

Compile mode transforms compiler invocations into libtool objects. It rejects user-specified `-o`, derives `.lo` and `.o` names from source suffixes, builds PIC objects when shared libraries are enabled, builds ordinary objects when static libraries are enabled, and creates a placeholder `.lo` when shared objects are disabled.

Link mode is the largest section. It parses compiler/linker arguments, `.lo`, `.o`, `.a`, `.la`, `-L`, `-l`, `-rpath`, `-version-info`, `-release`, `-dlopen`, `-dlpreopen`, `-export-dynamic`, and static-link switches. It reads libtool archive metadata, resolves dependency libraries, constructs compile and finalize commands, handles hardcoded runtime paths, creates shared libraries, static archives, reloadable objects, wrapper scripts for uninstalled executables, and `.la` metadata files.

For dynamic symbol preloading, link mode can use `nm` plus `global_symbol_pipe` to generate a C source file containing `dld_preloaded_symbols`, compile it, and link it into the executable.

Install mode wraps install/cp behavior for `.la` libraries, `.lo` objects, static archives, and libtool wrapper scripts. It installs shared library real names and symlinks, pseudo-library `.la` files, optional static archives, and may relink wrapper executables on platforms requiring installation-time hardcoding.

Finish mode runs platform-specific post-install commands such as `ldconfig` and prints instructions for runtime library paths. Execute mode sets the configured shared-library path variable, resolves wrapper scripts to uninstalled binaries, and runs a command. Uninstall mode removes `.la`-associated shared libraries, symlinks, dynamic-load names, and static archives.

The script depends on variables supplied by `ltconfig`: compiler/linker commands, object directory, archive commands, install hooks, naming specs, hardcode settings, runtime path variables, and build mode flags. It is portable shell build machinery and not runtime JPEG or filesystem code.
