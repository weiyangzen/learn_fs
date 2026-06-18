# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/dns.c

Implements DNS message-cache services on top of Unbound’s message cache and RRset cache.

Storage path:
- `dns_cache_store()` copies regional reply data into malloc/cache-owned storage, fixes reply flags for cache use, and stores either only referral rrsets or a full message plus rrsets.
- `dns_cache_store_msg()` converts relative TTLs to absolute TTLs, stores rrsets, handles TTL-zero messages, removes stale message-cache entries for TTL-zero answers, sorts rrset refs, and inserts message replies into the slabhash message cache.
- `store_rrsets()` updates/inserts rrsets into the RRset cache, prefers better cached rrsets when available, and adjusts message TTL/prefetch/serve-expired TTL to the minimum cached rrset TTL.

Lookup path:
- `msg_cache_lookup()` hashes query info plus flags, returns a locked message-cache entry if present and unexpired.
- `dns_cache_lookup()` first tries exact message-cache hits, then synthesizes answers from cached DNAME, CNAME, DS/DNSKEY rrsets, harden-below-NXDOMAIN data, or common RRsets for type ANY.
- `tomsg()` converts cached message entries back into region-allocated `dns_msg` replies with relative TTLs, checking rrset availability, CNAME-chain validity, and secure-message rrset security consistency.
- Supports serve-expired logic by allowing expired messages only when configured and permitted by reply metadata.

Delegation support:
- `dns_cache_find_delegation()` finds closest cached NS rrset, creates a delegation point, optionally synthesizes a referral message, adds DS/NSEC data, and fills A/AAAA glue from cache.
- `find_closest_of_type()` walks upward through qname labels looking for cached NS or DNAME rrsets, with optional checks that no expired rrsets exist above the found point.
- `cache_fill_missing()` fills missing nameserver A/AAAA addresses and negative address-cache entries into an existing delegation point.
- `find_add_addrs()` and `find_add_ds()` populate referral additional/authority sections from rrset/message caches.

Message synthesis:
- `dns_msg_create()` creates an unpacked region-allocated DNS message with a fixed rrset capacity.
- `dns_msg_authadd()` and `dns_msg_ansadd()` copy rrsets into authority/answer sections and update TTL.
- `rrset_msg()` builds a one-rrset answer from cached CNAME/DS/DNSKEY-like rrsets.
- `synth_dname_msg()` builds DNAME plus synthesized CNAME responses, handles TTL-zero upstream DNAME grace, YXDOMAIN on excessive synthesized name length, and carries DNAME security state to the caller.
- `fill_any()` returns either RFC8482-style NOTIMPL when `deny_any` is configured or a limited set of cached common RR types.

Serve-expired and prefetch:
- When serve-expired is enabled, `dns_cache_store()` avoids overwriting useful expired validated entries with unchecked validator-pending data, while updating no-recursion retry TTLs for error responses.
- `dns_cache_prefetch_adjust()` extends a cached message’s prefetch TTL under write lock.

Filesystem/storage relevance:
- No filesystem code. This is core cache infrastructure: slabhash message cache, RRset cache, TTL conversion, regional/malloc ownership transitions, lock ordering, and synthesis of resolver-visible DNS messages from cached records.
