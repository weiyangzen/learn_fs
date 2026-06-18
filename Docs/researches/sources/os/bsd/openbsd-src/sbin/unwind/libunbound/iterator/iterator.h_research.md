# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iterator.h

`iterator.h` declares the iterator module's public internal API, resolver limits, global iterator environment, per-query iterator state, qname-minimisation states, resolver states, and prepend-list structure.

`struct iter_env` stores process-wide iterator settings: IPv4/IPv6 availability, NAT64 prefix state, do-not-query and private-address/domain structures, caps-for-ID whitelist, dependency depth, target-fetch policy, ratelimit counter/lock, outbound retry count, send cap, and CNAME restart cap.

`struct iter_qstate` is the core per-query state record. It tracks the current/final iterator state, recursion depth, active response, answer/authority prepend lists, chased query name, outgoing query info, current delegation point, outstanding target/direct query counters, restart/referral/send counts, shared target counters, NXNS fallback marker, parent-side glue state, DS parent search state, DNSSEC expectation/lame flags, priming/refetch flags, qname minimisation state, auth-zone fallback flags, parse/scrub failure counters, and last failing upstream address.

The header exports the module hook functions: `iter_get_funcblock()`, `iter_init()`, `iter_deinit()`, `iter_operate()`, `iter_inform_super()`, `iter_clear()`, `iter_get_mem()`, plus state helpers. Changes here affect the iterator implementation and any module-stack code that creates, clears, or introspects iterator state.
