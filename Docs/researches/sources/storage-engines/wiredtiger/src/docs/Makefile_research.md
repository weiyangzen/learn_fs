# sources/storage-engines/wiredtiger/src/docs/Makefile

## Purpose
Small make wrapper for WiredTiger documentation generation.

## APIs and control flow
The default `all` target changes to `../../dist` and runs `sh s_docs -t`, which likely builds targeted documentation output. `clean` runs `sh s_docs -a`, likely a broader rebuild/cleanup mode. Both targets are marked phony.

## State, dependencies, integration, risks
It has no persistent state beyond artifacts produced by `dist/s_docs`. It depends on relative repository layout from `src/docs` to `dist`, POSIX shell, and the `s_docs` script. Tests/signals are make invocation from `src/docs`, correct relative path resolution, and ensuring generated docs are cleaned or rebuilt by the intended `s_docs` flags.
