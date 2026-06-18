# File Research: sources/os/bsd/openbsd-src/sbin/iked/parse.y

Read completely: 3391 lines.

Defines the yacc grammar, lexer, macro/include handling, address/transform parsing, policy/user/RADIUS construction, and helper routines for iked configuration files. It parses `ikev2` rules and selected global settings while intentionally skipping IKEv1/manual-keying/ipsec.conf legacy rules.

Static configuration defaults and maps:
- Global parser state tracks current environment, debug/rule counters, default passive/decoupled/MOBIKE/fragmentation/vendor-ID/OCSP/RADIUS settings, DPD interval, and certificate partial-chain behavior.
- Default IKE and ESP transform arrays provide authenticated and AEAD/noauth proposal sets.
- Transform name maps cover auth, PRF, IKE encryption, IPsec encryption, DH groups (including MODP/ECP/Brainpool/Curve25519/sntrup hybrid names), ESN, auth methods, SA protocols, and configuration payload attributes.
- `ipsec_addr_wrap`, `ipsec_hosts`, `ipsec_filters`, and `ipsec_mode` are parser-local structures for address lists, flow endpoints, tag/tap options, and grouped transform lists.

Grammar:
- Top-level grammar accepts includes, global `set` statements, local `user` credentials, `ikev2` rules, `radius` settings, macro assignments, and ignored IKEv1/manual rules.
- `set` updates active/passive, couple/decouple, fragmentation, MOBIKE, vendor ID, single-IKESA enforcement, sticky-address, OCSP URL/timing, cert partial chain, and DPD interval.
- `ikev2rule` gathers name, flags, SA protocol, address family, IP protocols, rdomain, flow hosts, peers, IKE/child SA transforms, IDs, lifetimes, auth, config payload options, interface, and filters, then calls `create_ike()`.
- `cfg` supports `config` and `request` CP attributes resolved through `cpxfs`.
- Host rules support `from/to`, reverse `to/from`, optional ports, peer/local endpoint constraints, `any`, `dynamic`, CIDR suffixes, and flow NAT syntax on source hosts only.
- Transform grammar builds lists for auth/encryption/PRF/group/ESN and distinguishes `ikesa` from `childsa` by switching the active encryption transform map.
- Auth grammar supports default signature-any, PSK inline/file, EAP RADIUS/MSCHAPv2, and explicit RSA/ECDSA/RFC7427/signature methods.
- Lifetime parsing supports numeric seconds, `m`/`h` time suffixes, byte suffixes `K`/`M`/`G`, and optional byte lifetime.
- Filters support PF tags and `tap encN` interface syntax; `iface` supports sec(4)-style routed IPsec policies.
- RADIUS grammar configures auth/accounting servers, retry/failover counts, config-attribute mapping, DAE listener, and DAE clients, zeroing secrets after use.
- Macro assignment rejects whitespace in macro names and stores values with `symset()`.

Lexer, includes, and macros:
- `yyerror()` reports filename and line number and increments file error counts.
- `lookup()` maps sorted keywords to parser tokens, returning `STRING` for non-keywords.
- `igetc()`, `lgetc()`, `lungetc()`, and `findeol()` implement nested include EOF behavior, line continuations, pushback, quote handling, and error recovery to end of line.
- `yylex()` skips whitespace/comments, expands `$macro` values using sentinel bytes to prevent recursive expansion, parses quoted strings with limited escapes, parses signed numbers with strict delimiters, and parses bare strings while excluding grammar punctuation.
- `check_file_secrecy()` requires config/secret files to be owned by root/current user and not group-writable/world-accessible in unsafe ways.
- `pushfile()` opens stdin or named files, enforces secrecy for included/secret files, initializes pushback buffer, and appends to the include stack.
- `popfile()` closes/frees a file and propagates its error count to the previous file.
- `parse_config()` resets parser globals, applies command-line passive option, runs `yyparse()`, transfers parsed globals into `env`, warns when no rules were loaded, frees macros/interface cache, and returns failure on parse errors.
- `symset()`, `cmdline_symset()`, and `symget()` manage persistent and config-local macro values.

Address, key, and transform helpers:
- `parsekey()`/`parsekeyfile()` parse PSK hex data from inline strings or secret files with `KEYSIZE_LIMIT`, secrecy checks, and explicit zeroing at grammar call sites.
- `get_id_type()` infers ASN.1 DN, IPv4, IPv6, user FQDN, or FQDN ID type.
- `host()` tries interface, numeric IP, then DNS parsing; `host_ip()` handles numeric host/CIDR; `host_dns()` expands DNS answers; `host_if()`, `ifa_load()`, `ifa_exists()`, `ifa_grouplookup()`, and `ifa_lookup()` expand interface names and groups from `getifaddrs()`/ioctl state.
- `host_any()` and `host_dynamic()` create special wildcard/dynamic wrappers later expanded per address family.
- `set_ipmask()` fills default IPv4/IPv6 mask lengths.
- `parse_xf()` does prefix-style transform name lookup with optional key length matching.
- `encxf_noauth()`, `keylength_xf()`, and `noncelength_xf()` expose transform properties to other code.
- `copy_transforms()` either copies explicit transform selections into policy proposals or falls back to defaults of the requested transform type.

Policy construction:
- `create_ike()` validates protocol count, names, interfaces, ID sizes, peer/local address-family constraints, active-mode peer requirements, and local/peer derivation from peer or host lists.
- It builds default or explicit IKE proposals, rejecting IKE group `none`, ESN on IKE SAs, mixed implicit/non-implicit authentication transforms, and auth transforms paired with AEAD/noauth encryption.
- It builds default or explicit child SA proposals with analogous implicit-auth checks and optional ESN transforms.
- It expands every source/destination host and protocol combination into outbound `iked_flow` records, expanding `any`/`dynamic` into IPv4 and/or IPv6 concrete addresses as needed.
- It copies configuration payload address options into fixed policy config slots up to `IKED_CFG_MAX`.
- It derives certificate request type from authentication method, logs selected auth, sends policy and flow data through `config_setpolicy()`/`config_setflow()`, increments the rule count, then frees all parser-owned intermediate structures.
- `create_flow()` creates one outbound flow, including optional pre-NAT source address, and inserts it into the policy RB tree while ignoring duplicates.
- `expand_flows()` expands AF_UNSPEC endpoints into concrete address-family combinations and preserves original wrapper AF values.
- `expand_keyword()` maps `any` and `dynamic` wrappers to `0.0.0.0/0`, `0.0.0.0`, `::/0`, or `::`.
- `create_user()` validates non-empty bounded username/password, sends the user to config, increments rule count, and zeroes the temporary record.
- `iaw_free()` frees linked address wrappers and any nested source-NAT wrapper.

Risks and notes:
- `parse_xf()` uses prefix matching; ambiguous prefixes rely on transform table ordering.
- DNS names may expand to multiple address wrappers and IPv6 DNS plus netmask is rejected.
- Link-local IPv6 interface addresses are skipped because scope handling is not supported there.
- `parse_config()` frees `ocsp_url` and later assigns the parsed pointer into `env->sc_ocsp_url`; ownership is parser-global/environment-sensitive.
- Some grammar failures call `err()`/`fatalx()` rather than returning parse errors, so malformed or unsupported system state can terminate the process.
