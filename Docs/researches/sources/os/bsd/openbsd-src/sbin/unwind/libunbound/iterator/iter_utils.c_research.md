# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_utils.c

`iter_utils.c` is the iterator’s shared utility implementation. It parses target-fetch policy, builds caps-for-ID whitelist trees, applies NAT64 config, wires do-not-query/private-address state, and copies core iterator config into `iter_env`.

Server selection is a major part of the file. `iter_filter_unsuitable()` rejects bogus, do-not-query, unsupported address-family, lame, or unresponsive targets; applies NAT64 synthesis for IPv4 targets when enabled; reads infra-cache RTT/lame state; and assigns penalty-weighted selection RTTs for parent-side lame, DNSSEC-lame, recursion-lame, and blacklisted servers. `iter_filter_order()` groups fast-enough targets, honors fast-server sampling and IPv4/IPv6 preference settings, and `iter_server_selection()` randomly chooses among the best candidates while tracking retry attempts.

The file also provides DNS message allocation/copy/store helpers, random probability selection for NS ordering, dependency-cycle detection for target address lookups, delegation-usefulness checks, and DNSSEC heuristics based on trust anchors, DS records, key-cache entries, and RRSIG presence.

Cache support includes storing parent-side NS/glue and negative parent-side entries, looking them back up to help last-resort resolution, and finding the next configured root class across hints and forwards atomically. Reply comparison for fallback sorts authority/additional rrsets canonically while preserving answer order.

Scrubbing-related helpers remove irrelevant DS records from referrals, strip NXDOMAIN answer sections for subdomain use, limit NSEC/NSEC3 TTLs to SOA TTL per RFC9077, and make replies minimal by removing authority/additional sections. Retry helpers decrement or merge address attempt counters across delegation-point refreshes.

Other notable APIs include `iter_stub_fwd_no_cache()` for finding closest stub/forward `no_cache` policy and returning the governing delegation name, plus `iterator_set_ip46_support()` for disabling iterator IPv4/IPv6 support based on available outbound interfaces.
