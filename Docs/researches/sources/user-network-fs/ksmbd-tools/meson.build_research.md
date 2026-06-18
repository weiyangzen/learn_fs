<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/meson.build -->
# sources/user-network-fs/ksmbd-tools/meson.build

## Purpose

Top-level Meson build definition for ksmbd-tools. It mirrors the autotools configuration in a Meson/Ninja graph.

## Important APIs, Types, and Functions

Declares the C project version by reading `include/version.h`, sets `gnu99`, creates common include directories, resolves GLib, libnl-genl, optional systemd, optional krb5, pthread, and config.h feature macros.

## Control Flow

Meson probes krb5 ABI members/functions when the feature dependency is found, computes `runstatedir`, installs `ksmbd.conf.example`, renders man pages and `ksmbd.service`, then enters addshare, adduser, control, mountd, and tools subdirectories.

## State and Persistence Behavior

Generates build-tree `config.h`, generated man pages, systemd unit, static libraries from subdirs, and final `ksmbd.tools` through the tools subdir.

## Dependencies and Integration Points

Requires Meson >=0.61.5, GLib >=2.58, libnl-genl >=3.0, pthread, optional krb5, optional systemd pkg-config variables, and subdir Meson files.

## Risks and Edge Cases

The `runstatedir` fallback contains a disabled version check and defaults through localstatedir/run. Meson and autotools must stay behaviorally identical for package consumers.

## Test Signals

`meson setup`, `meson compile`, and `meson dist` with krb5 disabled, enabled with MIT, and enabled with Heimdal dependency naming.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/meson.build -->
