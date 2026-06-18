# sources/test-tools/xfstests-bld/kernel-build/install-kconfig

Purpose: installs a suitable kernel `.config` into the external kbuild directory, selecting a baseline config by architecture and kernel version and layering optional debug/test fragments.

Important options: `--perf`, `--blktests`, `--i386`, `--arm64`, `--arch`, `--dept`, `--kasan`, `--kcsan`, `--lockdep`, `--ubsan`, `--full-debug-info`, `--extra-debug`, `--generic`, `--get-config-fn`, and `--no-action`.

Control flow: sources `arch-funcs`, canonicalizes architecture, verifies kernel source root, gets build dir from `kbuild --get-build-dir`, reads `make kernelversion`, searches backward for the newest matching config fragment, appends architecture and optional fragments, backs up existing `.config`, writes the new config, appends tag-derived `CONFIG_LOCALVERSION`, and runs `make olddefconfig`.

State/persistence: writes `$BLD_DIR/.config`, may create `$BLD_DIR/.config.bak`, and modifies local version based on `# TAG:` lines. Does not modify git-tracked kernel sources directly.

Dependencies/integration: integrated with `kbuild`, `kernel-configs`, Linux kernel `Makefile`, `MAINTAINERS`, make, awk/sed, and cross-compile helpers.

Risks: config search stops at version 2 and assumes numeric minor versions. `tags` are read from the generated config even in no-action mode, where the file may not exist. Fragment ordering controls final Kconfig values and should be deliberate.

Test signals: `--get-config-fn`, no-action dry runs, and a successful `make olddefconfig` for each supported architecture validate behavior.
