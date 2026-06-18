# sources/user-network-fs/nfs-ganesha/src/include/conf_url.h

## Purpose
`conf_url.h` defines the pluggable configuration URL interface used by config parsing to fetch configuration content from non-local backends, currently shaped around `rados://` URLs.

## Important APIs, Types, And Functions
`struct gsh_url_provider` is the provider registration object with a list node, provider name, lifecycle hooks (`url_init`, `url_shutdown`), and `url_fetch`. Public functions are `config_url_init`, `config_url_shutdown`, `register_url_provider`, `config_url_fetch`, and `config_url_release`. The header also declares RADOS watch helpers `gsh_rados_url_setup_watch` and `gsh_rados_url_shutdown_watch`.

## Control Flow
The implementation initializes a provider list, an rwlock, a simple URL regex, and conditionally loads `libganesha_rados_urls.so`. Providers register themselves with `register_url_provider`; `config_url_fetch` regex-matches the scheme and dispatches to the matching provider's `url_fetch`; `config_url_release` closes the returned `FILE *` and frees the backing buffer.

## State And Persistence
State lives in `conf_url.c`: a global provider list, rwlock, compiled regex, and optional dlopen handle. Fetches may materialize remote content into a buffer and `FILE *` stream. Persistent backing storage is provider-specific; this generic layer only owns transient fetch buffers and dynamic library state.

## Dependencies And Integration Points
It depends on `gsh_list.h`, `stdio.h`, `regex`, `dlfcn`, logging, and optional RADOS URL module symbols. It integrates with the parser's ability to read config from URLs and with RADOS URL watch setup during service registration.

## Risks
`register_url_provider` sets `code = EEXIST` on duplicate names but still calls `url_init` and adds the new provider, so duplicate registration behavior is hazardous. The regex only recognizes `rados://`, so adding schemes requires implementation changes. `config_url_release` uses `free(fbuf)` while most of the tree uses `gsh_free`; provider allocation must match this contract. URL fetch output ownership must be followed exactly to avoid leaks or double frees.

## Test Signals
Tests should cover initialization/shutdown idempotence, duplicate provider registration, malformed URLs, quoted and unquoted `rados://` strings, missing RADOS backend library, failed provider fetch, successful fetch/release, and concurrent fetch/registration behavior under the provider rwlock.
