<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/meson.build -->
# sources/user-network-fs/ksmbd-tools/mountd/meson.build

## Purpose

Build-system description for the `mountd Meson` component in ksmbd-tools.

## Important APIs, Types, and Functions

Creates static library `mountd` from worker, IPC, generic RPC, SRVSVC, WKSSVC, SAMR, LSARPC, security descriptor, and daemon sources; renders `ksmbd.mountd.8`; installs symlink.

## Control Flow

Meson builds all daemon support into one static library with GLib and libnl dependencies, configures the man page, and creates the command symlink.

## State and Persistence Behavior

Build static library and generated man page; install man page and symlink. Runtime daemon state is outside the build file.

## Dependencies and Integration Points

Requires top-level `include_dirs`, `glib_dep`, `libnl_dep`, runstatedir, and config.h.

## Risks and Edge Cases

RPC and IPC source omissions would produce runtime feature gaps. Build parity with Makefile.am is important for packaging.

## Test Signals

Meson compile/dist and `ksmbd.mountd --help`; runtime IPC tests require the kernel module.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/meson.build -->
