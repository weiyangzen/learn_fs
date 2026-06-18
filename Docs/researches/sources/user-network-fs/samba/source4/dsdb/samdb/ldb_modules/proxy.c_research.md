# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/proxy.c

## Purpose

`proxy.c` implements an LDB module named `proxy` that can forward selected search requests from the local database to an upstream LDB/LDAP server. It reads an `@PROXYINFO` control record containing upstream URL, credential, old/new base DNs, and string rewrite lists. Searches under the configured local base are translated to the upstream base, executed synchronously, then returned records are rewritten back into the local namespace.

The source comment explicitly describes the module as an investigation hack for MMC support, so it should be treated as legacy/experimental code rather than a hardened general proxy layer.

## Important APIs, Types, And Functions

`struct proxy_data` is module-private persistent state. It holds the upstream `ldb_context`, configured old and new base DNs, and old/new string rewrite lists. `struct proxy_ctx` is per-request callback state containing the module and original request, plus an optional debug count.

Key functions:

- `load_proxy_info()` lazily loads `@PROXYINFO`, initializes `proxy->upstream`, configures credentials, parses DN/string rewrite settings, and connects upstream.
- `proxy_convert_blob()` replaces the first case-insensitive occurrence of one byte-string with another inside an `ldb_val`.
- `proxy_convert_value()` applies all configured old-to-new rewrites to a value.
- `proxy_convert_tree()` converts a search filter from local strings to upstream strings, currently returning after the first replacement.
- `proxy_convert_record()` rewrites result DNs from `olddn` to `newdn` and applies value rewrites to every attribute value.
- `proxy_search_callback()` handles upstream replies, converts entries, ignores referrals, and completes the original request.
- `proxy_search_bytree()` decides whether a search should be proxied, translates base DN/filter/attributes, builds an upstream search request, runs it, waits synchronously, and propagates upstream errors.
- `proxy_request()` dispatches search requests to `proxy_search_bytree()` and passes other operations through.
- `ldb_proxy_module_init()` registers the module.

## Control Flow

On every request, `proxy_request()` only intercepts `LDB_REQ_SEARCH`. `proxy_search_bytree()` passes through special/no-base searches and searches outside `proxy->newdn`. For eligible searches, it calls `load_proxy_info()` on demand. That function searches local base `@PROXYINFO`, extracts `url`, `olddn`, `newdn`, `username`, `password`, `oldstr`, and `newstr`, initializes an upstream LDB context using the current event context, guesses credentials from loadparm, sets the configured username/password, and connects to the URL.

For proxied searches, the module creates a per-request context, converts the filter from local strings to upstream strings, copies the local base DN, removes the local base components, appends the upstream base, builds an upstream search request with original scope/attrs/controls, and sends it to `proxy->upstream`. The code then calls `ldb_wait(..., LDB_WAIT_ALL)`, making the module effectively synchronous despite LDB callback plumbing.

`proxy_search_callback()` converts each upstream entry and sends it to the original request. Upstream referrals are ignored. On done, it completes the original request successfully. Errors complete the original request with upstream controls/response/error.

## State And Persistence Behavior

`proxy_data` is intended to cache upstream connection and rewrite configuration for the module lifetime. `load_proxy_info()` checks `proxy->upstream != NULL` to avoid reloading. On load failure it frees parsed DNs and upstream context and resets `proxy->upstream` to `NULL`.

The module does not persist new local records. It reads local configuration from `@PROXYINFO`, maintains an in-memory upstream connection, and streams converted upstream search results to callers. It does not implement add, modify, delete, rename, transaction, or init methods in this file.

## Dependencies And Integration Points

The module uses LDB core request/callback/build APIs, `ldb_module.h`, Samba credentials (`cli_credentials_init`, `cli_credentials_guess`, username/password setters), talloc, string-list helpers, and loadparm opaque data. Its configuration contract is the local `@PROXYINFO` record with attributes documented in the file header.

Integration is narrow: consumers must place the `proxy` module in an LDB module stack and provide an initialized `struct proxy_data` as module private data. The source shown does not include an `init_context` function that allocates that private data, so either another layer is expected to set it or this module is incomplete as standalone code.

## Risks And Edge Cases

The code has several correctness and robustness risks. `proxy_search_callback()` calls `ldb_module_get_private(module)` even though no `module` variable is in scope; it should use `ac->module`, so the shown source would not compile unless a macro or outer symbol unexpectedly exists. `proxy_search_bytree()` logs fields from `newreq` before `ldb_build_search_req_ex()` initializes it, another apparent bug. `proxy_convert_blob()` assumes the caller already found a match; if called with no match it would subtract a null pointer. It treats `ldb_val` as string data for `strcasestr()`, so binary or non-NUL-terminated values are unsafe. `proxy_convert_record()` has two identical loops over attribute values, apparently duplicating rewrite work rather than separately handling DN syntax.

Configuration validation is weak. The error message says `oldstr` and `newstr` are required, but the actual null check only requires URL, DNs, username, and password before calling `str_list_make()` on `oldstr`/`newstr`. The old/new rewrite lists are not checked for equal length. Filter conversion returns after one replacement, so multiple occurrences or multiple mappings are not fully rewritten. Upstream work is synchronous and can block the local LDB request path. Credentials are stored in an LDB control record and copied into memory.

## Test Signals

Searches for `@PROXYINFO` and `ldb_proxy` in the local tree show only this source file, so there are no obvious dedicated tests. Any meaningful test should construct an LDB stack with a valid `@PROXYINFO`, verify local-base searches are forwarded to a temporary upstream DB, verify DNs/filter strings/value strings are rewritten both directions, and verify non-search or out-of-base requests pass through. A compile/build test is important because the callback and logging issues are syntactic/compile-time signals in this file.
