# sources/distributed-fs/tahoe-lafs/src/allmydata/cli/grid_manager.py

## Purpose

This Click-based CLI manages Tahoe Grid Manager configuration, identity keys, storage-server entries, and signed certificates for servers.

## Important APIs, Types, And Functions

`grid_manager` is the root Click group and requires `--config/-c`, either a directory or `-` for stdin/stdout-style config. The nested `Config` object lazy-loads the grid manager via `load_grid_manager()`. Commands are `create`, `public_identity`, `add`, `remove`, `list`, and `sign`. `_config_path_from_option()` converts a path string to `FilePath` or `None`.

## Control Flow

The root command stores a lazy config object in `ctx.obj`. `create` creates and saves a new grid manager. `public_identity` prints the public key. `add` decodes a storage node public key and saves the updated config. `remove` removes the server and deletes certificate files named `{name}.cert.{n}` from the config directory. `list` prints server keys and certificate validity relative to `current_datetime_with_zone()`. `sign` creates a certificate with a bounded expiry in days, prints JSON, and writes the next available certificate file when config is directory-backed.

## State And Persistence

Persistent state is the grid-manager configuration directory or stdin/stdout-backed config represented by `None`. Commands mutate and save grid manager state, remove old cert files, and create new certificate files atomically enough for `FilePath.create()` to reject existing names.

## Dependencies And Integration Points

It depends on Click, Twisted `FilePath`, Tahoe Ed25519 helpers, `abbreviate_time`, `allmydata.grid_manager`, and `jsonbytes`. `pyproject.toml` exposes it as the `grid-manager` console script.

## Risks

The command named `list` shadows the built-in, hence the noqa. Removing a server deletes sequential certificate files only until the first missing index, so sparse certificate files can remain. `add` assumes ASCII public-key input and maps duplicate names to ClickException. `sign` writes certificate JSON after printing it; filesystem failure can leave printed-but-not-saved certificates. Expiry is capped at five years by CLI policy.

## Test Signals

Use Click's test runner for create/add/remove/list/sign/public-identity, cover `--config -`, duplicate/missing server errors, invalid public keys, certificate file collision handling, sparse cert cleanup behavior, and expiry formatting for valid and expired certificates.
