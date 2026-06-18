# File Research: sources/virtualization/spdk/module/event/subsystems/iobuf/iobuf_rpc.c

Adds startup/runtime JSON-RPC support for iobuf options and stats.

Key elements:
- Registers startup RPC `iobuf_set_options`.
- Decodes optional pool counts, buffer sizes, and NUMA enable flag.
- Uses an X-macro field list shared between RPC context and `spdk_iobuf_opts`.
- Includes a static assert that `spdk_iobuf_opts` remains size 40.
- Registers runtime RPC `iobuf_get_stats`.
- Serializes per-module small and large pool cache/main/retry/cache-size stats.

Dependencies:
- SPDK iobuf option/stat APIs, JSON-RPC, string helpers, generated RPC context definitions.

Research notes:
- The static assert intentionally forces updates when `spdk_iobuf_opts` grows.
