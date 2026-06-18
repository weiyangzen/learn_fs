<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/winbind/wscript_build -->
# sources/user-network-fs/samba/source4/torture/winbind/wscript_build

## Purpose

This Waf build fragment defines the `TORTURE_WINBIND` internal smbtorture module.

## Important APIs, Types, and Functions

- `bld.SAMBA_MODULE('TORTURE_WINBIND', ...)` declares sources, generated prototype header, subsystem, init function, dependencies, and internal-module status.

## Control Flow

The fragment is executed during Samba's build configuration. It compiles `winbind.c`, `struct_based.c`, and the libwbclient test source into the `smbtorture` subsystem, generating `proto.h` and using `torture_winbind_init` as the module initializer.

## State and Persistence Behavior

It generates build artifacts only as part of the Waf build. It does not affect runtime state.

## Dependencies and Integration Points

Dependencies include `popt`, `wbclient`, `torture`, `PAM_ERRORS`, and `winbindd-lib`. The parent `source4/torture/wscript_build` recurses into this directory so the module becomes part of `smbtorture`.

## Risks and Edge Cases

If `winbindd-lib` or libwbclient tests change ABI or dependencies, this fragment must stay synchronized. The module is internal to smbtorture, not independently installed.

## Test Signals

Successful build should produce the `TORTURE_WINBIND` module with generated prototypes and visible `winbind` torture tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/winbind/wscript_build -->
