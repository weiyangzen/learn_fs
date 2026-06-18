# File Research: sources/virtualization/nbd/args.c

This file contains a refactored argument parser for `nbd-client`.

`init_client()` initializes a `CLIENT` with defaults: block size 512, one connection, default port `10809`. `free_client_fields()` currently resets the struct to defaults rather than freeing individual strings, explicitly noting this is test-oriented behavior.

`parse_nbd_client_args()` uses `getopt_long_only()` to parse command-line and old-style positional options. It handles connection target fields, block size, forced size, check/disconnect/list/version actions, export name, read-only, persist, preinit, timeout, dead connection timeout, Unix socket mode, TLS files/hostname/priority, and netlink-only options `identifier`/`nonetlink` when compiled with netlink support.

The parser returns a `parse_result_t` carrying immediate actions and errors rather than exiting directly. It also recognizes nbdtab-style invocation where a single `nbdX` or `/dev/nbdX` argument implies config lookup later in `nbd-client.c`.

Notable integration detail: some options are parsed as no-op placeholders for tests, including systemd mark and nofork. The parser accepts `-S` in the short option string but has no explicit switch case for it, so SDP command-line behavior should be checked against older parser behavior and documentation.
