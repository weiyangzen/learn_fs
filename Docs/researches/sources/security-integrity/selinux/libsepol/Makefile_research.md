# sources/security-integrity/selinux/libsepol/Makefile

## Purpose
This top-level libsepol Makefile orchestrates recursive builds, installs, cleaning, relabeling, and tests for the libsepol source tree.

## Important Targets and Variables
`DISABLE_CIL ?= n` controls whether CIL support is disabled and is exported to sub-makes. Targets are `all`, `install`, `relabel`, `clean`, and `test`. `all` builds `src` and `utils`; `install` descends into `include`, `src`, `utils`, and `man`; `relabel` runs only in `src`; `clean` descends into `src`, `utils`, and `tests`; `test` runs `make -C tests test`.

## Control Flow
The file is a simple recursive make dispatcher. Each target invokes `$(MAKE) -C <dir>` in a fixed order.

## State and Persistence Behavior
This Makefile does not directly create artifacts; subdirectories produce libraries, tools, installed files, cleaned outputs, relabeling effects, or test results. Exporting `DISABLE_CIL` affects subdirectory build configuration.

## Dependencies and Integration Points
It integrates libsepol's include, source, utility, manual, and test subtrees. External dependencies are the platform `make` and whatever each child directory requires.

## Risks and Test Signals
Because commands are sequential, an early sub-make failure stops later directories. There is no `.PHONY` declaration in this file, so files named after targets could interfere on some make implementations. Main signals are successful recursive `make`, `make install`, `make clean`, and `make test` invocations.
