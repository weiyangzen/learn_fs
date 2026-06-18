<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/Makefile.am -->
# sources/user-network-fs/ksmbd-tools/mountd/Makefile.am

## Purpose

Build-system description for the `mountd autotools` component in ksmbd-tools.

## Important APIs, Types, and Functions

Defines `libmountd.a` from worker, IPC, RPC service, security descriptor, and daemon sources; renders `ksmbd.mountd.8`; installs `ksmbd.mountd` as a symlink to `ksmbd.tools`.

## Control Flow

Automake compiles the daemon static library and generated man page. Install hooks create the command symlink used by the systemd unit.

## State and Persistence Behavior

Install state is man page and symlink. Runtime state is created by mountd code in runstatedir and netlink/kernel state.

## Dependencies and Integration Points

Requires GLib and libnl flags plus generated config macros for optional Kerberos and paths.

## Risks and Edge Cases

This source list must include all RPC service files and stay synchronized with Meson. Missing libnl flags break IPC compilation.

## Test Signals

Autotools distcheck, link test through `ksmbd.tools`, and `ksmbd.mountd --help` dispatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/Makefile.am -->
