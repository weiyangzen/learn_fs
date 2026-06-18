# sources/user-network-fs/nfs-utils/support/nfsidmap/Makefile.am

Purpose: Automake manifest for libnfsidmap and its mapping plugins.

Important build outputs: builds shared `libnfsidmap.la`, plugin modules `nsswitch.la`, `static.la`, `regex.la`, and optional `umich_ldap.la`/`gums.la`. Installs headers `nfsidmap.h` and `nfsidmap_plugin.h`, man pages, and `libnfsidmap.pc`.

Control flow: plugin directory comes from `PATH_PLUGINS` or defaults to `$(libdir)/libnfsidmap`. LDAP, GUMS, and LDAP SASL support are conditional. The core library links `-ldl` and `support/nfs/libnfsconf.la`; plugins that use config also link `libnfsconf.la`.

State and persistence: no runtime state; controls build/install layout and pkg-config metadata generation.

Dependencies and integration: integrates dynamic plugin loading with the core library and config parser. `dist-hook` copies Debian packaging files into release tarballs.

Risks: plugin build flags must match optional dependencies or runtime loading will fail. `gums.la` is built without `nfsidmap_common.c`, unlike other plugins, so it depends on the symbols it actually references being available through headers/libraries. Plugin directory affects runtime search behavior.

Test signals: build all optional combinations, verify plugin install paths, run `pkg-config --libs --cflags libnfsidmap`, and load each plugin through `libnfsidmap.c`.
