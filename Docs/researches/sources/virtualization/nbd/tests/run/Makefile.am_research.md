# File Research: sources/virtualization/nbd/tests/run/Makefile.am

## Purpose
Defines runtime integration tests for the NBD server and client test tooling.

## Main Contents
- Selects `cwrap_test` when socket-wrapper support is enabled, otherwise `simple_test`.
- Registers runtime tests such as config loading, write, flush, integrity, directory config, listing, readonly write failure, treefiles, Unix sockets, inetd, handshake, TLS, netlink connect/status, and persist mode.
- Builds `nbd-tester-client` from `nbd-tester-client.c` plus generated/copied `cliserv.c`, and optional TLS sources.
- Builds `libnl_mock.so` from `libnl_mock.c` for netlink-related tests.
- Distributes transaction traces and TLS certificate fixtures.

## Dependencies
Uses Automake conditionals `GNUTLS` and `CWRAP`, GLib flags/libs, optional GnuTLS flags/libs, and libnl flags/libs for the mock.

## Risks and Notes
`XFAIL_TESTS` is supplied by configure-time `@RUN_XFAIL@`. Several target names are empty rules used as Automake test labels.
