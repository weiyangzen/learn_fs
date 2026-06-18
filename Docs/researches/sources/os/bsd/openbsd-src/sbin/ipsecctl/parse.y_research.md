# File Research: sources/os/bsd/openbsd-src/sbin/ipsecctl/parse.y

This is the yacc grammar, lexer, and rule-construction core for `ipsecctl` configuration parsing.

Key responsibilities:
- Parses `ipsec.conf`-style statements for IKE rules, flow rules, static SAs, TCP MD5 SAs, includes, and macro assignments.
- Defines supported authentication, encryption, compression, and DH group transforms via `authxfs`, `encxfs`, `compxfs`, and `groupxfs`.
- Converts parsed syntax into `struct ipsec_rule` instances and appends expanded rules through `ipsecctl_add_rule`.
- Handles include stacks, macro expansion, lexical scanning, quoted strings, comments, numbers, and keyword lookup.
- Enforces config file secrecy for the top-level file and key files.
- Resolves host specifications from numeric IPv4/IPv6, DNS, interface names, interface groups, and `any`.
- Expands `any` into IPv4 and IPv6 wildcard networks.
- Validates address-family combinations, transform/key compatibility, SPI ranges, port/protocol constraints, NAT syntax, and static-key restrictions.
- Builds reverse flow and reverse SA rules for bidirectional declarations.
- Supports SA bundles by creating `RULE_BUNDLE` entries connecting sequential destination/SPI pairs.
- Supports `ike interface secN ...` rules by marking IKE rules with `IPSEC_RULE_F_IFACE` and storing the interface unit.

Important functions and data:
- `parse_rules()` initializes parsing, pushes the top file, invokes `yyparse`, and frees macros.
- `yylex()`, `lgetc()`, `lungetc()`, and `findeol()` implement the scanner and pushback handling.
- `pushfile()`/`popfile()` manage nested include files.
- `symset()`, `symget()`, and `cmdline_symset()` implement macros.
- `host()`, `host_v4()`, `host_v6()`, `host_dns()`, `host_if()`, `ifa_lookup()`, and `ifa_grouplookup()` resolve rule endpoints.
- `parsekey()` and `parsekeyfile()` parse hex key material.
- `create_sa()`, `create_flow()`, `create_ike()`, `reverse_sa()`, `reverse_rule()`, and `create_sabundle()` construct in-memory rules.
- `expand_rule()` performs host-list cross-product expansion and inserts concrete rules.
- `validate_sa()` applies protocol-specific transform/key rules.

Notable behavior:
- ESP defaults to AES encryption and HMAC-SHA2-256 authentication when omitted where appropriate.
- AH defaults to HMAC-SHA2-256 authentication.
- IPCOMP defaults to deflate compression.
- Static keys reject transforms marked as `nostatic`, including AEAD/CTR-style entries that require non-static handling.
- AEAD transforms reject explicit separate authentication.
- Port-specific flows require TCP or UDP protocol.
- Flow types default to `require` for AH/ESP and `use` for IPIP/IPCOMP.
- The parser accepts macros with `$name` substitution and warns about unused macros at high verbosity.
- Key file length is capped by `KEYSIZE_LIMIT`.

Dependencies:
- Consumes structures and constants from `ipsecctl.h`.
- Feeds parsed rules into the broader `ipsecctl` rule queues.
- Uses OpenBSD networking APIs such as `getifaddrs`, interface group ioctls, `getaddrinfo`, and `inet_net_pton`.

Research notes:
- This file is the semantic bridge between user configuration and the PF_KEY emission layer.
- It combines parsing, validation, expansion, and memory ownership logic in one large module, so changes to config syntax often have direct rule-generation consequences.
