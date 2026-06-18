# sources/test-tools/kdevops/scripts/kconfig/mconf-cfg.sh

## Purpose
This shell script discovers compiler and linker flags for ncurses so the Makefile can build the `mconf` menuconfig frontend.

## Important APIs, Types, And Functions
It takes two positional output files: a cflags file and a libs file. It checks `$HOSTPKG_CONFIG` for `ncursesw` then `ncurses`, then probes common include directories, then tests whether `$HOSTCC -E` can include `<ncurses.h>`.

## Control Flow
With `set -eu`, it aborts on missing variables or failed unguarded commands. Successful detection writes compiler flags to the cflags path and linker flags to the libs path, then exits 0. If all checks fail, it prints an explanatory error and exits 1.

## State And Persistence
The script writes the two files passed by the Makefile. It reads host include paths and uses environment variables `HOSTPKG_CONFIG` and `HOSTCC`.

## Dependencies And Integration Points
It is invoked by the Kconfig Makefile pattern rule for `mconf-cflags` and `mconf-libs`. It integrates with pkg-config and host C compiler discovery.

## Risks And Test Signals
Unset `HOSTCC` can fail the final fallback under `set -u` if pkg-config and include checks do not succeed. Include directory checks are distro-specific. Tests should run with fake/pkg-config-controlled environments, with only `/usr/include/ncursesw`, only `/usr/include/ncurses`, compiler fallback, and a no-ncurses failure case.
