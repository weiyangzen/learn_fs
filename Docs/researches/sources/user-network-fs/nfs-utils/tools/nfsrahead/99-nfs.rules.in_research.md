<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsrahead/99-nfs.rules.in -->
# sources/user-network-fs/nfs-utils/tools/nfsrahead/99-nfs.rules.in

## Purpose

`99-nfs.rules.in` is the install-time template for the generated udev rule that calls `nfsrahead`.

## Important APIs, Types, and Functions

It uses `_libexecdir_` as a substitution token in `PROGRAM="_libexecdir_/nfsrahead %k"` and assigns stdout to `ATTR{read_ahead_kb}="%c"`.

## Control Flow

Automake's rule in `Makefile.am` substitutes `_libexecdir_` with `@libexecdir@` to produce `99-nfs.rules`, which udev later evaluates on bdi add events.

## State and Persistence Behavior

The template has no runtime state. Its content controls the persistent installed udev rule generated during build.

## Dependencies and Integration Points

It depends on the build system substitution rule and udev's `PROGRAM`/`%c` behavior. It integrates the helper with kernel bdi sysfs tuning.

## Risks and Edge Cases

Any mismatch between substitution, configured `libexecdir`, and actual helper installation will break runtime invocation. The template assumes bdi `read_ahead_kb` exists and can be written by udev.

## Test Signals

Tests should check substitution output for configured prefix/libexecdir values and confirm the rule calls the installed helper path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsrahead/99-nfs.rules.in -->
