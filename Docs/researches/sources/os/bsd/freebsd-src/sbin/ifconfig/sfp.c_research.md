# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/sfp.c

`sfp.c` implements SFP/QSFP/CMIS transceiver status printing for ifconfig. It exposes `sfp_status(if_ctx *ctx)` for use by the wider ifconfig status path.

The function fetches module identity with `ifconfig_sfp_get_sfp_info()`, converts it to display strings, prints physical spec and connector, then fetches and prints vendor name, part number, serial number, and date.

Compliance output depends on module type and verbosity: CMIS skips legacy compliance, QSFP can show revision, and classic SFP can show class, length, technology, media, and speed at high verbosity.

Runtime diagnostic status prints module temperature, voltage, and per-lane RX power/TX bias using `power_mW()`, `power_dBm()`, and `bias_mA()`. Status resources are freed with `ifconfig_sfp_free_sfp_status()`.

At verbosity above 2, the module dumps raw EEPROM/page bytes using `hexdump()`, with different ranges for CMIS, QSFP/SFF8436, and SFP/SFF8472.

Dependencies include `libifconfig_sfp`, SFF8436/SFF8472 headers, and `libutil` hexdump support. The function returns silently when SFP data is unavailable.
