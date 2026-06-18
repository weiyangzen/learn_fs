<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcCommand.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcCommand.cc

## Purpose

`XrdPfcCommand.cc` implements internal `/xrdpfc_command/...` URLs used to create or remove cache files for testing, maintenance, and purge validation.

## Important APIs, Types, And Functions

- `Cache::ExecuteCommandUrl()` is the command dispatcher.
- `SplitParser` tokenizes command URL path components.
- `create_file` supports options `-h`, `-s filesize`, `-b blocksize`, `-t access_time`, and `-d access_duration`.
- `remove_file` supports `-h` and removes a cache file through `UnlinkFile(..., true)`.
- The create path uses `Info` metadata, `XrdOss` create/open calls, `posix_fallocate()`, resource monitor registration, and write-queue accounting.

## Control Flow

`Cache::Prepare()` schedules a `CommandExecutor` job for command URLs. The executor calls `ExecuteCommandUrl()`, which requires the first token to be `xrdpfc_command`, then dispatches on the command token. `create_file` parses an option subfield, validates size and block size with `XrdOuca2x`, creates data and `.cinfo` files, preallocates the data file, marks all blocks synced in `Info`, writes synthetic access records, adjusts metadata mtime, and registers synthetic resource-monitor stats. `remove_file` parses options and calls `UnlinkFile()` with `fail_if_open=true`.

## State And Persistence

`create_file` persistently creates data and `.cinfo` files in configured OSS data/meta spaces and writes cache metadata. It also mutates write-queue and resource monitor accounting. `remove_file` persistently unlinks cache data and metadata if the file is not open.

## Dependencies And Integration Points

It depends on `XrdPfcInfo`, `XrdPfcPathParseTools`, `XrdPfcResourceMonitor`, `XrdOfsConfigPI`, `XrdOss`, `XrdOuca2x`, `XrdOucEnv`, `XrdOucStream`, and fallocate/time APIs. It is reachable only when `pfc.allow_xrdpfc_command` is enabled.

## Risks And Edge Cases

- Command URLs can create large files up to 32 GiB; enabling the feature in production is risky.
- `access_time` and `access_duration` arrays have fixed `MAX_ACCESSES` length, but repeated `-t`/`-d` parsing does not visibly guard overflow.
- Error cleanup is partial: failures after data-file creation may leave stale files.
- The command interface relies on path token formatting with placeholder spaces between separators.
- The example Python script is embedded in a block comment and is Python 2 style.

## Test Signals

Tests should cover disabled command handling in `Prepare()`, malformed command URLs, help options, missing path/options, size/block bounds, mismatched access time/duration counts, repeated access records, refusal to overwrite existing `.cinfo`, cleanup on intermediate failures, resource monitor updates, and `remove_file` behavior for open and closed files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcCommand.cc -->
