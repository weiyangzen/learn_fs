# sources/test-tools/kdevops/scripts/kconfig/nconf-cfg.sh

## Purpose
`nconf-cfg.sh` detects compiler and linker flags needed to build the ncurses-based `nconf` frontend. It writes cflags and libs to output files provided as arguments.

## Important APIs, Types, And Functions
The script takes two positional arguments: output cflags path and output libs path. It checks `${HOSTPKG_CONFIG}` for `ncursesw menuw panelw`, then `ncurses menu panel`, then falls back to default include locations under `/usr/include`.

## Control Flow
With `set -eu`, the script first probes pkg-config. If wide-character ncurses packages exist, it writes their flags and exits. Otherwise it tries non-wide packages. If pkg-config is unavailable or unhelpful, it tests three header paths and emits hardcoded flags. On failure it prints installation guidance and exits nonzero.

## State And Persistence
Persistent output is limited to the two generated flag files. No temporary files or environment mutations are used.

## Dependencies And Integration Points
Depends on shell, `command -v`, optional pkg-config via `HOSTPKG_CONFIG`, and installed ncurses/menu/panel development headers/libraries. Build rules call this before compiling `nconf.c` and `nconf.gui.c`.

## Risks And Edge Cases
`HOSTPKG_CONFIG` is referenced under `set -u`; callers must define it or the script will fail. Positional arguments are not validated. Nonstandard ncurses installations without pkg-config files and outside checked include paths will fail.

## Test Signals
Run with `HOSTPKG_CONFIG=pkg-config` on systems with `ncursesw`, with only `ncurses`, and with no headers. Verify output files contain usable flags and that missing dependencies produce a clear nonzero failure.
