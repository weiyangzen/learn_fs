# sources/distributed-fs/tahoe-lafs/src/allmydata/util/configutil.py

## Purpose

This module reads, writes, copies, and validates Tahoe configuration files using `ConfigParser`. It normalizes UTF-8 with optional BOM, supports non-strict duplicate options, atomically-ish writes configs, and provides a composable `ValidConfiguration` contract for rejecting unknown sections/options.

## APIs and control flow

`get_config()` reads a file with `utf-8-sig` and delegates to `get_config_from_string()`. `set_config()` creates sections as needed. `write_config()` writes to a Twisted `FilePath` temporary sibling, creates parent directories, removes the target first on Windows, then moves the temp into place. `validate_config()` iterates all sections/options and raises `UnknownConfigError` for anything outside a `ValidConfiguration`.

`ValidConfiguration.everything()`, `.nothing()`, `.is_valid_section()`, `.is_valid_item()`, and `.update()` combine static valid sections with dynamic predicates. `copy_config()` clones values while escaping `%` to avoid interpolation effects.

## State, dependencies, risks, and tests

State is the returned `ConfigParser` and validation objects; persistence is `tahoe.cfg` on disk. Dependencies include `ConfigParser`, attrs, Twisted `platform`, and `FilePath` APIs. Integration points include node creation, provider configuration, and config validation.

Risks include Windows non-atomic overwrite behavior, `strict=False` accepting duplicate config entries, interpolation `%` handling, and predicate composition accidentally allowing too much. Test signals should cover BOM input, unknown section/option errors, atomic write paths, Windows target removal behavior, config copying with `%`, and merged validators.
