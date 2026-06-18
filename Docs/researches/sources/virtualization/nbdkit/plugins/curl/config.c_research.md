# File Research: sources/virtualization/nbdkit/plugins/curl/config.c

This file owns most configuration parsing and libcurl easy-handle setup for the curl plugin. It stores global options for URL, CA paths, cookies, cookie/header scripts, redirects, headers, HTTP version, IP resolution, credentials, protocol allowlists, proxy settings, TLS versions/ciphers, TCP options, timeout, Unix sockets, user, and user-agent.

`curl_config` parses each supported parameter, including password reads, boolean parsing, protocol parsing for old and new curl APIs, validation of unsupported proxy CA options, and rejection of cookiefile/cookiejar `-` to avoid stdin/stdout interaction. `curl_config_complete` requires `url` and rejects conflicting static/script header or cookie configuration and renew settings without scripts.

`allocate_handle` creates a `struct curl_handle`, initializes a libcurl easy handle, installs private data, verbose debug callback, error buffer, URL, signal/redirect/fail behavior, and every configured curl option. It prepares the handle for later read/write setup. `free_handle` cleans up the easy handle and any copied headers. `curl_dump_plugin` reports compile-time and dynamic curl versions/protocols. `debug_cb` routes verbose curl text and headers into `nbdkit_debug`, optionally including connection/transfer ids.

Risks and invariants: configuration is global across all handles. The `resolve` branch appends to `headers` rather than `resolves`, which looks like a likely bug because `CURLOPT_RESOLVE` later receives `resolves`. Security-sensitive options such as `sslverify=false` and protocol allowlists directly affect what remote resources can be accessed.
