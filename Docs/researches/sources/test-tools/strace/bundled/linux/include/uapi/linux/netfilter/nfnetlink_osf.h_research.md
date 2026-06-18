# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_osf.h

Purpose: defines passive OS fingerprinting ABI for netfilter OSF match support, including fingerprint records, matching flags, TCP option encoding, and add/remove nfnetlink messages.

Important APIs/types/functions: key types are `nf_osf_wc`, `nf_osf_opt`, `nf_osf_info`, `nf_osf_user_finger`, and `nf_osf_nlmsg`. Constants cover matching flags, log levels, TTL comparison modes, IANA TCP option kinds, window-size state machine values, OSF attributes, and `OSF_MSG_ADD/REMOVE`.

Control flow: userspace adds or removes OS fingerprints over nfnetlink. Packet matching compares IP/TCP header values, TTL/window/MSS wildcard rules, options, genre/version/subtype, and logs according to configured OSF info.

State/persistence behavior: fingerprint tables are persistent kernel netfilter state until removed. Match/log behavior affects later packet classification and logging but packet messages are transient.

Dependencies/integration: includes Linux IP/TCP header definitions and types. Integrates with nftables/iptables OSF expressions and netfilter packet path.

Risks and test signals: arrays sized by `MAX_IPOPTLEN` and multiple wildcard modes can be hard to render. Tests should decode add/remove messages, fingerprint strings, TTL/log flags, option arrays, window-size wildcard modes, and embedded IP/TCP headers.
