# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/module.c

Implementation helpers for the DNS module interface declared in `module.h`.

Key functions:
- Debug string helpers:
  - `strextstate(enum module_ext_state)`
  - `strmodulevent(enum module_ev)`
- Validation/servfail error-info collection:
  - `errinf(...)`
  - `errinf_ede(...)`
  - `errinf_origin(...)`
  - `errinf_rrset(...)`
  - `errinf_dname(...)`
  - `errinf_to_str_bogus(...)`
  - `errinf_to_reason_bogus(...)`
  - `errinf_to_str_servfail(...)`
  - `errinf_to_str_misc(...)`
- EDNS known-option management:
  - `edns_known_options_init(...)`
  - `edns_known_options_delete(...)`
  - `edns_register_option(...)`
  - `edns_option_is_known(...)`
  - `edns_bypass_cache_stage(...)`
  - `unique_mesh_state(...)`
  - `log_edns_known_options(...)`
- Inplace callback management:
  - `inplace_cb_register(...)`
  - `inplace_cb_delete(...)`
- Subquery state propagation:
  - `copy_state_to_super(...)` copies `was_ratelimited` upward only when the super state has not already recorded ratelimiting.

Important behavior:
- Error info is stored in the query's regional allocator and appended in order.
- Error-info collection is skipped unless validator log level is high enough or `log_servfail` is enabled.
- `errinf_to_reason_bogus` prefers the latest explicit EDE reason, but does not replace a more specific reason with generic `LDNS_EDE_DNSSEC_BOGUS`.
- EDNS option and inplace callback registration are rejected after workers exist (`env->worker` set), enforcing registration during module initialization.
- `edns_register_option` overwrites flags for an already registered option; otherwise it appends up to `MAX_KNOWN_EDNS_OPTS`.

Dependencies:
- `util/module.h`, `sldns/wire2str.h`, config, regional allocation, dname formatting, and `net_help` address formatting.

Research notes:
- `module.h` declares `inplace_cb_lists_delete`, but this paired implementation file does not define it.
