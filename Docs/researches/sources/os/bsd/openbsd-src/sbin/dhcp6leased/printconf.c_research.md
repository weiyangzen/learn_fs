# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/printconf.c

Configuration printer for `dhcp6leased`.

It renders the parsed configuration back as `dhcp6leased.conf` syntax. It prints `request rapid commit` when enabled, emits prefix-delegation request blocks per interface/IA, and prints each downstream interface target with its prefix length. At verbosity above one it also annotates derived prefix masks using the documentation prefix `2001:db8::`.
