# sources/test-tools/xfstests-bld/fstests-bld/build-all

Purpose: main build orchestrator for all component packages needed in the xfstests-bld appliance.

Important APIs and functions: shell functions `build_start()` and `set_skip_all()`, many `SKIP_*` flags, config loading, Android/cross-compile setup, reproducibility exports, and per-component build subshells.

Control flow: detects distro, sources config, sets Go/toolchain paths, handles cross/Android/static options, parses skip/only/clean/debug flags, sets `DESTDIR=bld`, builds Android compatibility if needed, then conditionally builds e2fslibs, popt, libaio, keyutils, fsverity, ima-evm-utils, util-linux, stress-ng, dbench, xfsprogs, fio, xfstests, quota, syzkaller, blktests, LTP, nvme-cli, and misc utilities.

State and persistence: creates `bld`, version `.ver` files, configured component trees, installed binaries/libraries/headers, and build-distro metadata. It mutates fetched repositories during configure/build.

Dependencies and integration: depends on `config`, fetched component repos, autoconf/automake/make, optional Go, cross toolchains, and component-specific build systems.

Risks: large script with many environment-sensitive branches. Static/cross/Android flags can interact subtly. Some paths patch upstream files with `ed` or remove generated files, so repeated builds must be tested.

Test signals: successful component builds, populated `bld`, generated version files, and no skipped required component unless explicitly configured.
