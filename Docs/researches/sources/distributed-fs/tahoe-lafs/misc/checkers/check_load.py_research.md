# sources/distributed-fs/tahoe-lafs/misc/checkers/check_load.py

## Purpose

This load-generating client randomly reads and writes through Tahoe WebAPI nodes, maintaining atomic stats files that can be aggregated by a separate `--stats` mode.

## Important APIs, Types, and Functions

Top-level config files are `server-URLs`, `root.cap`, `delay`, and `operation-mix`. `listdir` fetches `?t=json` directory metadata. `choose_random_descendant` recursively chooses a file. `read_and_discard` streams file bytes. `create_random_directory`, `generate_filename`, and `choose_size` generate write targets. `parse_url` is copied URL parsing. `generate_and_put` uses `httplib` to stream a zero-filled PUT.

## Control Flow

In `--stats` mode, the script samples stats files every ten seconds and prints per-second deltas plus a moving average. In load mode, it repeatedly sleeps, randomly selects read or write according to configured weights, chooses a server URL, performs the operation, updates counters, writes `stats_out.tmp`, and atomically renames it to `stats_out`.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is Tahoe grid content and the stats file. Dependencies are Python 2 networking modules, JSON WebAPI responses, and local config files. Integration is grid load testing and aggregate monitoring. Risks include infinite loops, no HTTP status validation after PUT, recursion into empty directories, bytes/text issues in Python 3 despite future annotations, and never incrementing `directories_written`. Tests should mock `urllib`/`httplib`, verify stats aggregation deltas, URL construction, atomic stats rename, and operation-mix selection.
