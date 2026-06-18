# sources/security-integrity/selinux/checkpolicy/test/Makefile

## Purpose

This Makefile builds the checkpolicy test utilities `dispol` and `dismod`. In this subset, `dismod.c` is the relevant companion source. The Makefile is intentionally small and assumes libsepol is available either as an explicit archive dependency or through linker search paths.

## Important Targets and Variables

`CFLAGS ?= -g -Wall -W -Werror -O2` supplies default strict compilation flags while allowing the environment to override them. `LIBSEPOLA` can name a specific `libsepol.a`; if unset, `LDLIBS_LIBSEPOLA := -l:libsepol.a` asks the linker to find the static archive by name.

`all` builds both `dispol` and `dismod`. Each executable links its object file, optional `$(LIBSEPOLA)`, normal `CPPFLAGS`, `CFLAGS`, `LDFLAGS`, and `$(LDLIBS_LIBSEPOLA)`. `clean` removes the two binaries and object files.

## Control Flow and Integration

The Makefile delegates compilation of `.c` to make's built-in suffix rules and defines only link commands. It is part of the checkpolicy test area and links directly against libsepol internals used by the utilities.

## State and Persistence Behavior

Build outputs are local binaries and `.o` files in the test directory. No generated source or persistent test data is managed here.

## Dependencies and Risks

The Makefile assumes a compiler, make built-in compile rules, and a linkable static libsepol archive. The indentation before `LDLIBS_LIBSEPOLA :=` is spaces in the conditional body; GNU make accepts it for variable assignment, but recipe lines still require tabs. `-Werror` can make builds sensitive to compiler-version warnings.

## Test Signals

Running `make` should produce `dispol` and `dismod`; `make clean` should remove them. A useful CI signal is building once with explicit `LIBSEPOLA=/path/to/libsepol.a` and once with only linker search paths.
