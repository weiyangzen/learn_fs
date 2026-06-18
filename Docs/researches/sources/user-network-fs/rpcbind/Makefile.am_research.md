# sources/user-network-fs/rpcbind/Makefile.am

## Purpose
Defines the Automake build for rpcbind and rpcinfo.

## APIs, Flow, And State
Sets `AUTOMAKE_OPTIONS`, common preprocessor flags, optional debug/warmstart/libwrap/rmtcalls flags, and program targets. `rpcbind_SOURCES` lists the daemon sources, `rpcbind_LDADD` links libtirpc and optional systemd libraries, and `rpcinfo` is built from `src/rpcinfo.c`. Man pages and optional systemd unit installation are declared.

## Dependencies And Integration
Consumes conditionals and substitutions from `configure.ac`: `DEBUG`, `LIBSETDEBUG`, `WARMSTART`, `LIBWRAP`, `RMTCALLS`, `SYSTEMD`, `TIRPC_*`, `statedir`, `rpcuser`, and `nss_modules`.

## Risks And Test Signals
Build failures can result from conditional drift with `configure.ac` or missing source lists. Test signal is autoreconf/configure/make success across option combinations and installation of expected units/manpages.
