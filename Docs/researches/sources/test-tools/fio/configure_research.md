## sources/test-tools/fio/configure

Purpose: fio's hand-written configuration script. It detects target OS/CPU/compiler/features, writes `config-host.mak` and `config-host.h`, and records probe details in `config.log`.

Important flow: the script creates temporary C/object/exe paths, installs a cleanup trap, removes old generated config files, parses many `--enable-*`/`--disable-*` options, chooses a compiler, detects target OS/CPU and endianness, then runs compile/link probes for atomics, word size, zlib, AIO variants, pthread features, fallocate/fadvise, affinity, clocks, network/socket helpers, storage engines, optional libraries, CUDA/cuFile, ISA-L, xnvme/libblkio/libnfs, valgrind, zoned block support, and compiler warnings. `output_sym()` appends both make variables and C defines. The tail emits selected `CONFIG_*` symbols, `LIBS`, `CFLAGS`, `LDFLAGS`, `CC`, install prefix, seed bucket count, and an out-of-tree forwarding Makefile when needed.

State and persistence: persistent outputs are `config-host.mak`, `config-host.h`, `config.log`, and possibly `Makefile`. It mutates shell variables as feature state and accumulates `LIBS`, `CFLAGS`, and `LDFLAGS`.

Dependencies and integration: every build consumes its generated config. CI build scripts call it with target-specific flags. Feature choices drive conditional compilation in files such as CRC acceleration, cgroups, zlib iolog support, engines, and platform helpers.

Risks and test signals: probes may pass/fail differently under cross-compilation because run tests are limited. Shell variables default lazily, so option spelling and environment values matter. Library order and package versions are fragile. Primary test signal is successful configure plus build/test across the CI matrix; `config.log` is the debugging artifact.
