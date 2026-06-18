## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_read_conf.c

Purpose: declares configurable 9P protocol parameters.

APIs and flow: defines global `_9p_param`, `_9p_params` config items for worker count, TCP/RDMA ports, msize, backlog, and RDMA pool sizes, plus `_9p_param_blk` for the `_9P` config stanza with DBus interface metadata and `noop_conf_commit`.

State/dependencies: persists configuration into `_9p_param` during config parsing. Depends on `config_parsing.h`, `gsh_config.h`, and constants in `9p.h`.

Risks/tests: test min/max validation, default values, singleton block enforcement, DBus/config reload behavior, and that negotiated msize defaults align with runtime buffer sizes.
