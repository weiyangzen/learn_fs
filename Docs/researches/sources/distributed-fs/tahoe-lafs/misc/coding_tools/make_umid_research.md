# sources/distributed-fs/tahoe-lafs/misc/coding_tools/make_umid

## Purpose

This script creates short random message IDs for Foolscap `umid=` logging arguments so incidents can be traced back to source code.

## Important APIs, Types, and Functions

`make_id` reads four random bytes, base64 encodes them, rejects IDs containing `/` or `+`, removes padding, and returns the six-character-ish ID. The optional first command-line argument is a count.

## Control Flow

The script defaults to one ID, parses a count if supplied, and prints that many generated IDs. It loops inside `make_id` until the base64 alphabet produces an acceptable value.

## State, Dependencies, Integration, Risks, and Tests

There is no persistence except stdout. Dependencies are `os.urandom` and base64. Integration is developer/editor workflows plus `check-umids.py`. Risks include Python 3 bytes/string mismatches (`"/" in m` where `m` is bytes), no uniqueness check against the repository, and probabilistic collisions. Tests should monkeypatch `os.urandom` to cover rejection and padding removal, and verify count handling.
