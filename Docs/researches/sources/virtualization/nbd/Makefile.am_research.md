# File Research: sources/virtualization/nbd/Makefile.am

Top-level Automake file for the NBD source tree.

It builds `nbd-server`, `nbd-trdump`, and `nbd-trplay` as installed binaries, with `nbd-client` and `make-integrityhuge` as conditional/extra programs. It defines internal libtool libraries `libnbdsrv.la`, `libcliserv.la`, and `libnbdclt.la`.

Client build behavior is conditional on `CLIENT` and `GNUTLS`. With GnuTLS, it builds both `nbd-client` with `crypto-gnutls.c`/`buffer.c` and `min-nbd-client` with `-DNOTLS`; without GnuTLS, `nbd-client` is compiled with `-DNOTLS`.

It wires parser generation for `nbdtab_parser.tab.h` via `bison`, distributes support files such as `maketr`, `CodingStyle`, `autogen.sh`, `README.md`, and `support/genver.sh`, and sets `AM_DISTCHECK_CONFIGURE_FLAGS=--enable-syslog`.
