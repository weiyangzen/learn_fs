# File Research: sources/os/plan9/9front/sys/src/cmd/replica/revproto.c

Reverse proto reader/enumerator. Parses proto files, walks a source root, maps paths into an external/rooted namespace, and invokes a callback for each discovered file.

Supports explicit entries, recursive `+`, one-level `*`, uid/gid/mode overrides, old path aliases, environment-variable expansion, indentation-based hierarchy, directory skipping after stat/open failures, and warnings through a callback.

Used by replica tools to enumerate client/server paths while preserving proto-derived metadata.
