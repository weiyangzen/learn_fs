# sources/security-integrity/selinux/python/sepolicy/sepolicy/network.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/network.py

Purpose: provides policy-query helpers for discovering which SELinux domains can bind or connect to TCP/UDP port types.

Important APIs and control flow: `get_types(src, tclass, perm, check_bools=False)` runs `sepolicy.search()` for allow rules matching a source, object class, and permissions, then returns unique target types whose permissions include the requested set and, optionally, whose conditional rules are enabled. `get_network_connect(src, protocol, perm, check_bools=False)` resolves port type records from `sepolicy.gen_port_dict()`, queries socket permissions such as `name_bind` or `name_connect`, normalizes generic pseudo-types (`port_t`, `port_type`, `unreserved_port_type`, `reserved_port_type`, `rpc_port_type`, `ephemeral_port_type`), and returns a dictionary keyed by `(src, protocol, perm)` mapping to `(port_type, port_list)` tuples.

State and persistence: no durable state; all data comes from live sepolicy policy query caches and generated port dictionaries.

Dependencies and integration points: imported by `manpage.py` for user network sections and likely by the `sepolicy network` CLI. It depends on allow-rule shape from `sepolicy.search()` and port records keyed by `(type, protocol)`.

Risks and test signals: the filtering of generic port types has subtle precedence rules and silently ignores port types missing from `portrecs`. Tests in `test_sepolicy.py` run `sepolicy network -l`, `-t http_port_t`, `-p 80`, and `-d httpd_t`, giving smoke coverage but not validating specific permission-to-port mappings.
