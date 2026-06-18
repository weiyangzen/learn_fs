# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/network.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/network.py

Purpose: template fragments for generated SELinux network port and packet policy.

Important APIs and control flow: declares `TEMPLATETYPE_port_t` through `corenet_port`, DNS and generic receive rules, TCP/UDP socket creation, bind/connect fragments for specific and broad port classes, and a large `if_rules` block defining public corenet interfaces for send/receive/bind/connect/dontaudit operations on the generated port type plus client/server packet send/receive/relabel interfaces. `te_rules` is empty because callers select specific fragments.

State and persistence: rendered into generated policy interfaces and type enforcement. Persistence is the generated module and port type definitions.

Dependencies and integration points: relies on corenet reference-policy macros and is consumed by `sepolicy generate` for services needing inbound/outbound network access.

Risks and test signals: broad fragments like `corenet_tcp_connect_all_ports` or bind-all templates can overgrant if selected casually. Packet interfaces expose lower-level packet relabel permissions. No direct tests validate generated network policy syntax or least-privilege choices.
