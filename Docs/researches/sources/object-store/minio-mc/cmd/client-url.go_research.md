# sources/object-store/minio-mc/cmd/client-url.go

## Purpose

`client-url.go` defines mc's internal URL representation and helpers for parsing aliased paths, object-storage URLs, filesystem paths, content-type guessing, stat lookup, and prefix checks. It is the glue between user-facing path syntax and the `Client` abstraction.

## Important APIs, Types, And Control Flow

`ClientURL` records type, scheme, host, path, scheme separator, and path separator. `newClientURL` parses `http://` and `https://` authorities as object storage, otherwise treats input as filesystem. `String` converts object-storage URLs to canonical slash-separated form, with Windows-specific path cleanup, and returns filesystem paths unchanged. `joinURLs` and `urlJoinPath` append paths after normalizing to slash separators.

`url2Stat` builds a client with `newClient`, derives alias-specific SSE keys, and calls `Stat`. `firstURL2Stat` lists recursively and returns the first match. `url2Alias` separates the alias from the path with Windows adjustments. `guessURLContentType` uses `mimedb` extension lookup. `urlParts` and `isURLPrefix` split paths and test whether source/destination should be considered nested, accounting for trailing separators and wildcard path parts.

## State, Dependencies, Integration, Risks, And Tests

This file has no durable state. It depends on `filepath`, `runtime`, `regexp`, `mimedb`, and client factory helpers from other files. Integration points include copy/mirror safety checks, stat calls, content-type defaults, and alias expansion. Risks are scheme parsing that accepts only alphabetic schemes despite the comment, Windows separator edge cases, mutation of `url1` in `joinURLs`, and prefix logic around wildcards. `client-url_test.go` covers URL parsing, URL joining, and symmetric prefix detection.
