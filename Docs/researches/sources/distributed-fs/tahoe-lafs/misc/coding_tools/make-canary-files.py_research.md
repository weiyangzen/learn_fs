# sources/distributed-fs/tahoe-lafs/misc/coding_tools/make-canary-files.py

## Purpose

This operational tool generates per-server canary files whose storage index permutation places the first share on a desired Tahoe storage node for a chosen convergence secret and node list.

## Important APIs, Types, and Functions

`Options` parses convergence path, nodeids path, `k`, `N`, and verbosity. `get_permuted_peers(key)` reproduces Tahoe peer permutation with `sha1(key + nodeid)`. `find_share_for_target(target)` repeatedly constructs random content, asks Tahoe upload code for the storage index, checks the first permuted peer, and writes a `canaries/<nodeid>-<nickname>.txt` file on success.

## Control Flow

The script reads base32 node IDs and optional nicknames, decodes the convergence secret, warns if non-default k/N is used, creates `canaries`, and searches independently for each target node. It uses a Deferred-returning upload helper but relies on synchronous completion by inspecting `d.result`.

## State, Dependencies, Integration, Risks, and Tests

Persistent state is the generated `canaries` directory and files. Dependencies are Tahoe internals, Twisted usage, base32 helpers, SHA-1 permutation, and local convergence/nodeid files. Risks include Python 2 string/bytes mismatches, infinite expected search time for bad assumptions, failure if `canaries` already exists, reliance on Deferred internals, and needing patched Tahoe encoding parameters for non-default k/N. Tests should fix node IDs/convergence, monkeypatch storage index generation, and verify filename sanitization and permutation targeting.
