# sources/user-network-fs/nfs-ganesha/src/config_parsing/conf_url.c

## Purpose

`conf_url.c` implements the generic URL-provider registry and dispatch layer for `%url` configuration includes. It currently recognizes `rados://` URLs and can dynamically load the RADOS URL provider module.

## Important APIs, Types, and Functions

Public functions are `register_url_provider`, `config_url_init`, `config_url_shutdown`, `gsh_rados_url_setup_watch`, `gsh_rados_url_shutdown_watch`, `config_url_fetch`, and `config_url_release`. Internal helpers include `init_url_regex`, optional `load_rados_config`, and `match_dup`.

## Control Flow

Initialization creates the provider list and lock, optionally loads `libganesha_rados_urls.so`, calls its package initializer, and compiles a URL regex. Providers register by name under a write lock and run their `url_init` callback. `config_url_fetch` matches the URL, extracts type and provider-specific path, finds a provider under a read lock, and calls its `url_fetch`. Shutdown removes providers, calls their shutdown callbacks, frees the regex, closes the dynamic module, and destroys the lock.

## State and Persistence Behavior

State is process-global: `url_rwlock`, `url_providers`, compiled `url_regex`, and optional dynamic-library handles/function pointers. Fetched URL content is returned as a `FILE *` plus backing buffer and must be released with `config_url_release`.

## Dependencies and Integration Points

It depends on POSIX regex, pthread rwlocks, `dlopen`/`dlsym`, Ganesha list/log/memory wrappers, and provider definitions from `conf_url.h`. The scanner's `%url` directive calls `config_url_fetch`, and daemon reload paths can call RADOS watch setup/shutdown wrappers.

## Risks and Edge Cases

`register_url_provider` calls `url_init` and adds the provider even after detecting a duplicate name, returning `EEXIST` but still mutating state. The URL regex only accepts `rados` and a narrow character set. Dynamic loading behavior differs under ASan/FreeBSD by avoiding `RTLD_DEEPBIND`. `config_url_release` uses `free` for `fbuf`, matching `open_memstream` but requiring providers to follow that convention.

## Test Signals

Initialize/shutdown with and without `RADOS_URLS`, fetch valid and invalid URLs, register duplicate providers, and run `%url` parser tests. Dynamic module loading should be tested in normal and ASan builds.
