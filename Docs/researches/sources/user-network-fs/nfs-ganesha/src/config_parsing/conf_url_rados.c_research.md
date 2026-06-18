# sources/user-network-fs/nfs-ganesha/src/config_parsing/conf_url_rados.c

## Purpose

`conf_url_rados.c` implements the dynamically loaded `rados://` configuration URL provider. It reads Ganesha config fragments from Ceph RADOS objects and can watch a configured object to trigger daemon reloads.

## Important APIs, Types, and Functions

Key public/module functions are `conf_url_rados_pkginit`, `register_service_to_ceph`, `rados_url_setup_watch`, and `rados_url_shutdown_watch`. Important internals are `rados_urls_set_param_from_conf`, `rados_url_client_setup`, `cu_rados_url_init`, `cu_rados_url_shutdown`, `rados_url_parse`, `cu_rados_url_fetch`, `rados_url_watchcb`, and the `rados_url_provider` instance. The config block is `RADOS_URLS` with `ceph_conf`, `userid`, and `watch_url`.

## Control Flow

Package initialization registers the provider. Early provider init compiles the RADOS URL regex. Full init loads the `RADOS_URLS` config block, creates a librados cluster, reads the Ceph config, connects, and marks the provider initialized. Fetch parses a URL into pool, optional namespace, and object, creates an ioctx, reads the object in 1024-byte chunks into an `open_memstream`, rewinds it, and returns the stream/buffer to the scanner. Watch setup parses `watch_url`, ensures a client connection, creates an ioctx, registers `rados_watch3`, and the callback acknowledges notifications then sends `SIGHUP` to the process.

## State and Persistence Behavior

State is module-global: compiled regex, `rados_t cluster`, `initialized`, watch ioctx/cookie/object, service-update thread, and parsed `rados_url_param`. The service registration path can start a heartbeat thread that periodically updates Ceph service status while initialized. Fetched config data persists in a memory stream until released by the generic URL layer.

## Dependencies and Integration Points

It depends on librados, pthreads, POSIX regex, signals, Ganesha config loading APIs, `RADOS_URLS` block descriptors, and the generic URL provider API. It integrates with Ceph FSAL/RADOS deployments where configs and recovery metadata live in Ceph.

## Risks and Edge Cases

`cu_rados_url_shutdown` joins the service update thread while `initialized` is still true, so the loop may not exit before join unless another path changes state. `rados_url_parse` allows object-only URLs even though the comment questions the lack of a default pool; passing a null pool to `rados_ioctx_create` is risky. The read loop's write accounting uses `MIN(nread, 1024)` rather than the actual `wrt`, which can mis-handle short writes. Error logging uses `strerror(ret)` even though librados returns negative errno values.

## Test Signals

Integration tests need a Ceph cluster or mocked librados: parse object-only, pool/object, and pool/namespace/object URLs; fetch multi-chunk objects; validate memory stream contents; test missing `RADOS_URLS`; test watch callback SIGHUP behavior; and exercise clean shutdown with the heartbeat thread enabled.
