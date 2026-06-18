# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/sbin/ver

Purpose: tiny helper for printing appliance or kernel version information.

Important behavior: two-line shell helper, likely used interactively or by scripts to show version state.

State and dependencies: no persistent state; depends on shell and whatever command it delegates to.

Integration points: operational convenience for test appliance debugging.

Risks and test signals: minimal risk; validation is simply that it executes in the appliance image and prints expected version output.
