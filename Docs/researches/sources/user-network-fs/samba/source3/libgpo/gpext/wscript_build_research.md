# sources/user-network-fs/samba/source3/libgpo/gpext/wscript_build

## Purpose

Defines Waf/Samba3 build targets for the `gpext` modules in this directory.

## Important APIs, Types, and Functions

Uses `bld.SAMBA3_MODULE` to define `gpext_registry`, `gpext_scripts`, and `gpext_security`. `gpext_registry` uses source `registry.c` and dependency `NDR_PREG`; the other two use `scripts.c` and `security.c`. All targets use subsystem `gpext`, an empty `init_function`, and module enable/static decisions from `SAMBA3_IS_ENABLED_MODULE` and `SAMBA3_IS_STATIC_MODULE`.

## Control Flow

The file is evaluated by Waf during configure/build. It has no runtime path; it describes which C files are compiled into Samba's extension subsystem depending on module configuration.

## State and Persistence Behavior

No runtime state exists. Persistent effects are build artifacts and module availability. The explicit `NDR_PREG` dependency is required for `registry.c` policy parsing.

## Dependencies and Integration Points

Integrates the GPO extension C files with Samba's source3 module infrastructure.

## Risks and Test Signals

Risks are build-time omissions or missing dependencies. Test signals are successful Waf configuration, expected module enablement, and link/load coverage for all three extensions.
