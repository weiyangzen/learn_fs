# File Research: sources/virtualization/nbd/args.h

Header for the refactored `nbd-client` argument parser.

It includes `config.h` and `nbdclt.h`, then defines `parse_result_t`, which reports parser exit code, error message, immediate action flags, check/disconnect/list/version state, and netlink-only fields when `HAVE_NETLINK` is enabled.

It declares `parse_nbd_client_args()`, `free_client_fields()`, and `init_client()`.
