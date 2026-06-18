# Research: sources/user-network-fs/rclone/fs/rc/cache_test.go

## sources/user-network-fs/rclone/fs/rc/cache_test.go

Purpose: unit tests for rc fs-resolution helpers and fscache endpoints. `mockNewFs` seeds the global cache with mock filesystems and an `ErrorIsFile` entry.

Control flow tests normal named fs lookup, missing parameters, structured config maps with `type` or `_name`, single-file resolution creating include filters, `getConfigMap` error and string generation cases, default `GetFs`, remote pairing helpers, and nested `fscache/entries`/`clear` rc calls. State is global cache content that is cleared via deferred cleanup, plus context-local filter replacement for single-file cases. Dependencies include `mockfs`, `cache`, `filter`, and testify. Integration signal is high because rc operations rely on these helper functions for every filesystem parameter. Risks covered include invalid structured config values, missing keys, active-filter incompatibility for single-file scopes, and cache clearing. Remaining gaps include config value quoting edge cases beyond the tested generated string.
