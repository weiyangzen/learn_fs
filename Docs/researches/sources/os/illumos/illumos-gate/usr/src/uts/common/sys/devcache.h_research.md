# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devcache.h

This kernel header defines the client-facing interface for cached `/etc/devices` nvlist-backed files. It includes list support.

`nvf_handle_t` is an opaque handle returned to clients that register a cache file. `nvf_ops_t` describes a cache file: path, unpack callback, pack callback, list-free callback, and write-complete callback.

Client interfaces include `nvf_register_file`, `nvf_read_file`, `nvf_wake_daemon`, `nvf_error`, `nvf_cache_name`, `nvf_lock`, `nvf_list`, `nvf_mark_dirty`, and `nvf_is_dirty`.

Research notes:
- This is kernel-only and supports clients such as devid cache and other device-state persistence.
- Clients own logical list contents but use the devcache framework for nvlist file persistence and daemon wakeups.
- Implementation details live in `devcache_impl.h`.
