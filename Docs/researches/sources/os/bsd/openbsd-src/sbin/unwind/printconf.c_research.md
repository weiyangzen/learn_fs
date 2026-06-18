# File Research: sources/os/bsd/openbsd-src/sbin/unwind/printconf.c

`printconf.c` serializes an in-memory `struct uw_conf` back into unwind configuration syntax. `print_config()` prints resolver preference order, plain and DoT forwarders, block-list settings, and force rules.

Plain forwarders omit `port 53`; DoT forwarders omit `port 853`, print an authentication name when present, and append `DoT`. Force rules are grouped by resolver type and emitted separately for normal and `accept bogus` entries by scanning the force RB tree for each resolver type.

This file is presentation-only: it does not validate or mutate configuration, but it depends on `uw_resolver_type_str`, forwarder TAILQs, and the force tree layout from `unwind.h`.
