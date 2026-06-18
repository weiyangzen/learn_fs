# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_hints.c

`iter_hints.c` implements Unbound iterator root/stub hint storage. It owns creation/destruction of `struct iter_hints`, a locked `name_tree` keyed by zone name and class, with `struct iter_hints_stub` values that wrap a `delegpt` plus the stub priming mode.

Configuration loading is handled by `hints_apply_cfg()`: it clears the existing tree under a write lock, reads configured root-hints files, reads configured stub zones, and falls back to compiled-in root server hints when no IN root hint exists. Compiled-in hints cover the root server IPv4/IPv6 addresses according to `cfg->do_ip4` and `cfg->do_ip6`.

Root-hints parsing uses `sldns_fp2wire_rr_buf()` and accepts NS/A/AAAA records, creating a delegation point with parent-side NS state. Stub parsing handles stub zone names, `stub-host` names, direct stub addresses, TLS auth names when supported, `stub-first`/prime behavior, `no_cache`, `ssl_upstream`, and `tcp_upstream`.

Lookup/update APIs include `hints_find()`, `hints_find_root()`, `hints_lookup_stub()`, `hints_next_root()`, `hints_add_stub()`, `hints_delete_stub()`, `hints_swap_tree()`, and `hints_get_mem()`. Several lookup functions intentionally leave the read lock held on successful returns unless `nolock` is set, matching the header’s caller-unlock contract.

Notable behavior: duplicate hint insertion logs and ignores the second hint while returning success; external add/delete rebuilds parent pointers with `name_tree_init_parents()`. The file is tightly coupled to iterator delegation-point management, config parsing, dname utilities, and root/stub resolution policy.
