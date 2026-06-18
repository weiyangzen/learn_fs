# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/dns.h

Header for DNS cache services.

Defines:
- `DNSCACHE_STORE_EXPIRED_MSG_CACHEDB`: store-policy flag allowing zero-TTL messages for cachedb-style behavior.
- `struct dns_msg`: region-allocated query info plus reply info wrapper.

Declares:
- `dns_cache_store()` and `dns_cache_store_msg()` for storing messages/rrsets into shared caches.
- `dns_cache_find_delegation()` for reconstructing delegation points and optional referral messages from cache.
- `tomsg()` for converting cached message entries to region-allocated messages with relative TTLs.
- `dns_msg_deepcopy_region()` for deep-copying messages into a region.
- `dns_cache_lookup()` for full cache lookup and synthesis.
- `cache_fill_missing()` for filling nameserver address data into delegations.
- `dns_msg_create()`, `dns_msg_authadd()`, and `dns_msg_ansadd()` for building unpacked cache responses.
- `dns_cache_prefetch_adjust()` to adjust prefetch timing.
- `msg_cache_lookup()` and `msg_cache_remove()` for lower-level message-cache access.

Role:
- Defines the contract between iterator/validator/module code and the DNS cache implementation.
- Makes explicit that returned cache messages are region allocated and that `msg_cache_lookup()` returns locked entries requiring caller unlock.
