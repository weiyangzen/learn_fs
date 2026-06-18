<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/monitoring/prometheus_exposer.cc -->
# sources/user-network-fs/nfs-ganesha/src/monitoring/prometheus_exposer.cc

## Purpose
This file implements a minimal Prometheus HTTP scrape endpoint for the Ganesha monitoring registry. It listens on an IPv4 or IPv6 socket, serializes collected Prometheus metric families, compacts empty metrics, tracks scrape latency success/failure, and optionally updates procps-backed memory/CPU gauges after scrapes.

## Important APIs, Types, and Functions
`SocketStreambuf` adapts a socket fd to `std::ostream` with a 4096-byte output buffer, blocking `send()` loops, abort tracking, and a mutex-protected `safe_close()`. `is_metric_empty()` and `compact_family()` remove zero-value counter, empty summary, and empty histogram children while retaining at least one child per family. `getBoundries()` returns scrape-latency histogram buckets.

`PrometheusExposer::start()` creates the server socket, sets `SO_REUSEADDR`, binds IPv4 or IPv6, listens, marks `running_`, and starts `server_thread`. `stop()` clears `running_`, shuts down the server fd to wake `accept4()`, joins the thread, closes the socket, and resets the fd. `server_thread()` accepts clients, reads one request buffer, collects/compacts registry families, writes an HTTP 200 text response, serializes metrics, closes the client, observes scrape latency, and calls `update_mem_info()` when procps and dynamic metrics are enabled.

Extern "C" wrappers are `prometheus_exposer__start()`, `prometheus_exposer__stop()`, and optional `update_mem_info()`.

## Control Flow
The server loop runs while `running_` is true. Each accepted connection is handled synchronously in the server thread; there is no per-client worker pool. HTTP parsing is intentionally minimal: it reads up to 1024 bytes and responds with metrics regardless of path or method. Serialization is through `prometheus::TextSerializer::Serialize()`.

`prometheus_exposer__start()` is idempotent with a static `initialized` flag. It casts the registry handle to a Prometheus registry pointer, constructs a static exposer, starts it, then marks initialized. `prometheus_exposer__stop()` has its own static `stopped` flag and constructs another static exposer before calling `stop()`.

## State and Persistence Behavior
Runtime state is in the `PrometheusExposer` instance: socket fd, running flag, thread object, and scrape latency histograms registered in the registry. Metrics persist in the registry; the HTTP endpoint itself persists only while the process is running. `SocketStreambuf` owns no fd but closes the accepted client through `safe_close()`.

## Dependencies and Integration Points
The implementation depends on POSIX sockets (`socket`, `setsockopt`, `bind`, `listen`, `accept4`, `recv`, `send`, `shutdown`, `close`), C++ stream and mutex primitives, `prometheus_exposer.h`, `dynamic_metrics.h`, `gsh_config.h`, prometheus-cpp-lite registry and serializer APIs, global `nfs_param.core_param.enable_dynamic_metrics`, and optional procps (`openproc`, `readproc`) for process resource metrics.

## Risks and Edge Cases
The start and stop C wrappers each declare a separate function-local static `PrometheusExposer exposer(*registry_ptr)`. That means `prometheus_exposer__stop()` does not obviously stop the instance created by `prometheus_exposer__start()`; it constructs/stops a distinct static object. This is a lifecycle risk and could leave the actual server running until process teardown.

Error handling uses `PFATAL`, `PEXIT`, and `abort()/exit(1)` inside a library component. Bind/listen/socket failures can terminate the whole daemon rather than returning an error to startup code. `server_thread()` handles clients serially, so a slow send can block all scrapes. `recv()` return values are ignored; malformed or empty requests still get a response. `accept4()` and `SOCK_CLOEXEC` are Linux-specific unless compat is provided elsewhere. `SocketStreambuf::sync()` treats `send()` returning 0 as progress of zero bytes and could loop indefinitely on unusual socket behavior.

`compact_family()` copies metrics by value in the lambda and removes empty metrics from a collected copy, which is safe for output reduction, but keeping the first empty child may still expose misleading labels. `update_mem_info()` calls `openproc()` but does not close the `PROCTAB`, which can leak per scrape if procps requires `closeproc()`.

## Test Signals
Tests should start the exposer on IPv4 and IPv6 loopback, scrape `/metrics`, verify content type and Prometheus text output, verify compacting retains one empty metric but removes additional empty children, observe success/failure scrape latency updates, and confirm stop actually closes the listening socket. Fault tests should cover bind failures, slow/disconnected clients, procps metric updates, and repeated start/stop calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/monitoring/prometheus_exposer.cc -->
