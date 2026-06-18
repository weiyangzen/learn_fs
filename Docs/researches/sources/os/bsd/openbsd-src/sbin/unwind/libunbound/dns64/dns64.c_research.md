# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dns64/dns64.c

Unbound DNS64 module implementation. It plugs into Unbound’s module chain and synthesizes AAAA answers from A answers when appropriate.

Configuration:
- Default DNS64 prefix is `64:ff9b::/96`.
- Accepts DNS64 prefix lengths 32, 40, 48, 56, 64, or 96.
- Supports `dns64_ignore_aaaa` tree for names whose real AAAA answers should be ignored and synthesized anyway.
- Supports `dns64_synthall`.

Core state:
- `enum dns64_state`: internal query, new external query, subquery finished.
- `struct dns64_qstate`: per-query state plus original `no_cache_store`.
- `struct dns64_env`: prefix address/net length and ignore-AAAA name tree.

Major functions:
- `dns64_init()` allocates module env and applies config.
- `dns64_deinit()` frees ignore-AAAA tree.
- `dns64_operate()` handles module events and controls query state.
- `handle_event_pass()` handles new queries, PTR rewrite cases, and forced synthesis cases.
- `handle_event_moddone()` decides whether a completed AAAA query needs an A subquery.
- `generate_type_A_query()` attaches an A subquery for an AAAA query.
- `handle_ipv6_ptr()` rewrites reverse IPv6 PTR queries under the DNS64 prefix into IPv4 PTR subqueries.
- `dns64_inform_super()` receives subquery completion and adjusts the parent query.
- `dns64_adjust_a()` converts A answer rrsets to AAAA rrsets and updates parent response.
- `dns64_adjust_ptr()` copies IPv4 PTR response and rewrites answer owner name to original IPv6 PTR qname.
- `dns64_synth_aaaa_data()` synthesizes one AAAA rrset from one A rrset for the configured prefix.

Cache behavior:
- New external queries force `qstate->no_cache_store = 1` while DNS64 determines whether to modify results.
- Synthesized responses may be stored if the query did not start as no-cache.
- Negative AAAA entries may be removed from rrset/msg cache when synthesized data replaces them.

Address synthesis:
- `synthesize_aaaa()` embeds IPv4 bytes at the configured prefix offset and skips byte 8.
- `extract_ipv4()` reverses that process for PTR handling.
- `ipv4_to_ptr()` builds wire-format `in-addr.arpa` names.

Role in group:
- Upstream-style single-prefix DNS64 module, contrasted with OpenBSD `dns64_synth.c`, which provides frontend multi-prefix synthesis for `unwind`.
