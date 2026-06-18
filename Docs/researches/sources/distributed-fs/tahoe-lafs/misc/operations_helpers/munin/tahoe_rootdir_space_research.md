# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/munin/tahoe_rootdir_space

## Purpose

This Munin plugin graphs the deep size of files reachable from a configured Tahoe root directory, as exposed by an external URL.

## Important APIs, Types, and Functions

It reads env `url`, expects the response body to be an integer, and emits `space.value`.

## Control Flow

Config mode prints one graph field. Normal mode fetches, strips, converts to `int`, and prints the value.

## State, Dependencies, Integration, Risks, and Tests

State is none. Integration depends on another service producing root-directory size. Risks include no timeout, unvalidated response text, and Python 2 urllib. Tests should cover config output, valid integer bodies, and invalid body failures.
