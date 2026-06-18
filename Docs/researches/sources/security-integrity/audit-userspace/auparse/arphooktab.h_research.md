# sources/security-integrity/audit-userspace/auparse/arphooktab.h

Purpose: Build-time table mapping ARP netfilter hook numbers to names.

Important APIs, types, and functions: Defines `_S(0, "INPUT")`, `_S(1, "OUTPUT")`, and `_S(2, "FORWARD")`. `auparse/Makefile.am` builds `arphooktabs.h` from it with `gen_arphooktabs_h --i2s arphook`.

Control flow: No runtime flow; generator macro expansion only.

State and persistence: Static source data converted into generated lookup code.

Dependencies and integration points: Values are tied to `include/uapi/linux/netfilter_arp.h` and feed auparse interpretation of ARP hook audit fields.

Risks and edge cases: Kernel changes or namespace-specific interpretations could require table updates. Wrong ordering would produce incorrect human-readable audit output.

Test signals: Indirect build-generation coverage and any interpretation tests for ARP hook fields.
