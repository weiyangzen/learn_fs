# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_utils.h

`iter_utils.h` declares the broad helper surface used by the Unbound iterator module. It includes constants limiting cache lookups for nameserver address fetching and parent-side glue fetching.

The API covers config application, target server selection, DNS message allocation/copy/cache storage, NS random probability, dependency-cycle marking, delegation usefulness checks, DNSSEC expectation and message-origin heuristics, reply equality, caps-for-ID fallback cleanup, parent-side cache storage/lookup, root-class iteration across hints/forwards, DS/NXDOMAIN scrubbing, retry accounting, stub/forward no-cache lookup, runtime IP-family support, fetch-policy parsing, caps whitelist management, NAT64 config, NSEC TTL limiting, and minimal-response conversion.

Because this header is included by iterator control code and related modules, changes to it affect selection, caching, DNSSEC decision-making, hardening behavior, and fallback mechanics across the resolver.
