# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/module.h

Core interface for Unbound DNS handling modules.

Major concepts:
- Modules are state machines run in sequence.
- The mesh drives query state machines, passes replies back from rightmost modules to leftmost modules, and handles recursive subqueries.
- Per-query allocations generally live in the query `regional`.
- `module_env` provides shared caches, config, services, time, random state, mesh access, and module-specific globals.

Key constants:
- `MAX_MODULE 16`
- `MAX_KNOWN_EDNS_OPTS 256`

Key types:
- `struct errinf_strlist`: linked validation/error explanation strings plus EDE reason.
- `enum inplace_cb_list_type`: reply/cache/local/servfail/query/query-response/EDNS-parsed callback list identifiers.
- `struct edns_known_option`: option code plus cache-bypass and aggregation flags.
- `struct inplace_cb`: linked registered callback entry.
- Callback typedefs:
  - `inplace_cb_reply_func_type`
  - `inplace_cb_query_func_type`
  - `inplace_cb_edns_back_parsed_func_type`
  - `inplace_cb_query_response_func_type`
  - `serve_expired_lookup_func_type`
- `struct module_env`: shared runtime environment with config, caches, infra/key caches, outbound query service, mesh subquery services, scratch memory/buffer, worker/outnet/mesh pointers, validation anchors, auth zones, forwards/hints/views/respip, module info, inplace callback lists, EDNS known options, module stack, cachedb flag, and `unique_mesh`.
- `enum module_ext_state`: initial, wait reply, wait module, restart next, wait subquery, error, finished.
- `enum module_ev`: new, pass, reply, no reply, caps fail, module done, error.
- `struct sock_list`: linked sockaddr list used for origins/blacklists.
- `struct serve_expired_data`: timer plus cached-answer lookup callback.
- `struct module_qstate`: per-query state including qinfo, flags, priming/validation-recursion flags, reply/return data, origins, blacklist, regional allocator, error info, current module, per-module ext states/minfo, mesh info, EDNS option lists, cache-control flags, ratelimit/refetch/cachedb/error-response state, client/respip/RPZ flags, TCP/drop flags.
- `struct module_func_block`: module lifecycle and per-query methods (`startup`, `destartup`, `init`, `deinit`, `operate`, `inform_super`, `clear`, `get_mem`).

Declared helper APIs:
- State/event stringification: `strextstate`, `strmodulevent`.
- Error-info append/format helpers.
- EDNS known-option allocation, registration, lookup, cache-bypass, mesh-uniqueness, and logging.
- Inplace callback registration/deletion/list deletion.
- `copy_state_to_super`.

Research notes:
- This is one of the central contracts of libunbound/unwind's recursive resolver pipeline.
- Function pointers declared here are protected elsewhere by the whitelist layer from `fptr_wlist.h`.
