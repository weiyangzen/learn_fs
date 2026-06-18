<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/semodule/Makefile -->
# sources/security-integrity/selinux/policycoreutils/semodule/Makefile

## Purpose
Builds and installs `semodule`, plus a `genhomedircon` symlink that reuses `semodule` behavior.

## Important APIs, Types, And Functions
Variables configure sbin/man destinations, libselinux/libsemanage include and library paths, `LIBSEMANAGE_LDLIBS`, `LIBSELINUX_LDLIBS`, and `SEMODULE_OBJS`. Targets are `semodule`, `genhomedircon`, `install`, `relabel`, and `clean`.

## Control Flow
`all` builds `semodule` and creates a local symlink named `genhomedircon`. `install` copies `semodule`, creates the installed symlink, installs both man8 pages, and installs localized man pages. `clean` removes the binary, objects, and symlink.

## State And Persistence
Build state is `semodule.o`, `semodule`, and symlinks. Install persists the management utility and compatibility entry point.

## Dependencies And Integration Points
Depends on libsemanage, libsepol, libselinux, and CIL logging through the linked libraries. The `genhomedircon` invocation is handled by `semodule.c` based on `argv[0]`.

## Risks And Edge Cases
The symlink target assumes both commands can share one binary. If packaging strips or renames one entry point, `argv[0]` behavior changes.

## Test Signals
Build/link success against libsemanage/libsepol, installed symlink correctness, `semodule -l`, and `genhomedircon` mode invocation are good signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/semodule/Makefile -->
