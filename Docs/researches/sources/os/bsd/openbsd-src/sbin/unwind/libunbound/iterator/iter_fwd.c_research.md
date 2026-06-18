# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_fwd.c

Implementation of Unbound forward-zone storage and lookup.

Data model:
- Forward zones are stored in an RB tree ordered by class and domain-name label ordering.
- Each `iter_forward_zone` may contain a malloc-backed `delegpt`.
- Entries with `dp == NULL` are “holes” for stub/auth zones that should override broader forward zones.
- Parent pointers are computed after tree changes to support closest ancestor lookup.

Core behavior:
- Create/delete `iter_forwards` with RW lock.
- Parse forward zone names, forward-host names, and forward-address entries from config.
- Configure delegation-point flags: `has_parent_side_NS`, `no_cache`, `ssl_upstream`, and `tcp_upstream`.
- Warn about forward-host circular dependency when host lies below forwarded zone.
- Add holes for configured stub zones and auth zones.
- Apply config by replacing the tree under write lock.
- Exact lookup via `forwards_find()`.
- Closest-encloser forwarding lookup via `forwards_lookup()`.
- Root forward lookup and iteration over root entries by class.
- Add/delete forward zones and stub holes dynamically.
- Swap internal trees for reload.

Important semantics:
- `forward-first` clears `has_parent_side_NS`, allowing fallback to internet nameservers after forwarder failure.
- Stub/auth holes deliberately stop a broader forward from catching names that should be handled by more specific configured zones.
- Locking can be skipped with `nolock` when caller already holds the appropriate lock.

Role in group:
- Resolver policy component that routes selected domains to configured upstream forwarders instead of normal iteration.
