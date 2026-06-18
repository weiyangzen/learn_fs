# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/conf.h

This header defines configuration defaults and the public configuration API.

Key contents:
- Root paths and default config/policy/certificate/keynote directories under `/etc/isakmpd/`.
- Default lifetime tags and values for main mode and quick mode.
- Default key length ranges for Blowfish and AES.
- General defaults such as retransmits, exchange max time, KeyNote usage, policy file, and Delete-SAs behavior.
- Default phase 1 configuration section and transform name.
- `struct conf_list_node` and `struct conf_list` for comma-separated config lists.
- Extern `conf_path`.
- Prototypes for transaction, accessor, initialization, reload, remove, set, free-list, match, and report functions.

Research notes:
- The header exposes the default configuration contract consumed by most daemon subsystems.
