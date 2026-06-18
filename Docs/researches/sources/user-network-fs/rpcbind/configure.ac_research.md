# sources/user-network-fs/rpcbind/configure.ac

## Purpose
Defines rpcbind's Autoconf configuration, feature toggles, dependency checks, and output files.

## APIs, Flow, And State
Initializes package `rpcbind` version 1.2.9, checks C compiler, defines enable options for libwrap, debug, warmstarts, and remote calls, defines with-options for state directory, rpc user, NSS module list, and systemd unit dir, checks libtirpc via pkg-config, tests abstract socket support in libtirpc, checks optional libsystemd or libsystemd-daemon, checks libwrap when requested, searches pthread support, checks `nss.h`, computes `_sbindir`, and outputs `Makefile` plus systemd unit files.

## Dependencies And Integration
Feeds Automake conditionals and substitutions consumed by `Makefile.am` and systemd templates. Depends on pkg-config, libtirpc, optional systemd/libwrap, and Autoconf macros.

## Risks And Test Signals
Risks include CPPFLAGS clobbering during the abstract-socket probe, optional dependency detection drift, and systemd default lookup when pkg-config lacks systemd. Test signal is configure success for default and enabled feature matrices.
