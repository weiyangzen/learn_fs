# sources/object-store/openstack-swift/swift/common/utils/config.py

## Purpose

`config.py` centralizes Swift configuration parsing and validation helpers. It converts string values from `.conf` files into booleans, numbers, percentages, request-node-count functions, fallocate reserve settings, reseller-prefix option maps, affinity sort/predicate functions, and section dictionaries from one config file or a directory of config files.

## Important APIs, Types, And Functions

- `TRUE_VALUES` defines string truth values: `true`, `1`, `yes`, `on`, `t`, and `y`.
- Boolean and numeric validators include `config_true_value()`, `non_negative_float()`, `non_negative_int()`, `config_positive_int_value()`, `config_positive_float_value()`, `config_float_value()`, `config_auto_int_value()`, and `config_percent_value()`.
- Ring/request behavior parsers include `config_request_node_count_value()` and `config_fallocate_value()`.
- Prefix helpers include `config_read_prefixed_options()`, `append_underscore()`, and `config_read_reseller_options()`.
- Ring-affinity helpers include `affinity_key_function()` and `affinity_locality_predicate()`.
- File readers include `read_conf_dir()`, `NicerInterpolation`, `readconf()`, and `parse_prefixed_conf()`.

## Control Flow And Behavior

The small validators parse input, enforce bounds, and raise `ValueError` with configuration-oriented messages. `config_auto_int_value()` returns a caller-provided default for `None` or `"auto"`, while `config_percent_value()` returns a fraction between `0.0` and `1.0`. `config_request_node_count_value()` returns a closure that maps replica count to either a constant or `N * replicas`.

Reseller-prefix flow reads `reseller_prefix`, treats `"''"` as an empty prefix, ensures prefixes end with underscores, deduplicates them, then builds per-prefix option dictionaries by applying unprefixed options followed by prefix-specific overrides. `config_read_prefixed_options()` recognizes list defaults by splitting lower-cased comma-separated values; scalar defaults are stripped strings.

Affinity flow parses strings such as `r1=1` or `r2z7=2`, builds matcher dictionaries, sorts by priority, and returns a key function that places matching ring nodes ahead of unmatched nodes. Locality flow parses strings such as `r1` or `r2z2` and returns a predicate that accepts ring nodes matching any configured region/zone.

`readconf()` chooses `RawConfigParser` when raw mode is requested and otherwise uses `ConfigParser` with `NicerInterpolation`. The custom interpolation bypasses interpolation work unless the value contains `"%("`, preserving common Swift values like `1%` while still allowing legacy interpolation. It preserves option-case with `optionxform = str`, reads from file-like objects, single files, or sorted `.conf` files in a directory, and returns either one section dict with `log_name` or an all-sections mapping plus `__file__`.

## State And Persistence

The module has no mutable persistent state beyond `TRUE_VALUES`. It reads configuration files and directories but does not write them. Returned dictionaries include `__file__` pointing back to the original `conf_path`.

## Dependencies And Integration Points

Dependencies are standard `os`, `operator`, `re`, and `configparser`. `__init__.py` re-exports these helpers. They are used throughout Swift: daemon and WSGI startup read `.conf` files and parse daemonization/fallocate/eventlet settings; servers and middleware parse booleans; storage policy code parses deprecation/default flags; proxy code parses behavior toggles; backend-rate-limit and keymaster middleware read specific config sections; ring and proxy logic use affinity functions.

## Risks And Edge Cases

- `config_true_value()` only returns true for literal `True` or recognized strings; numeric `1` is false unless represented as `"1"`.
- `config_fallocate_value()` indexes `reserve_value[-1:]`, so callers must pass a sliceable value, usually a string.
- `config_read_prefixed_options()` ignores falsey values entirely, so an explicit empty string cannot override a default.
- `config_request_node_count_value()` returns closures; callers must remember to call the returned function with replica count.
- Affinity parsing is strict and raises for malformed pieces; deployment typos can prevent service startup.
- `read_conf_dir()` reads sorted visible `.conf` files only, so hidden files and non-`.conf` suffixes are intentionally ignored.
- `readconf()` all-sections mode returns a nested mapping keyed by section names and also a top-level `log_name`, so callers must distinguish section names from metadata.
- `NicerInterpolation` preserves `1%`-style values by bypassing interpolation unless `"%("` is present; this is compatibility-sensitive.

## Test Signals

No local tests are available in this source snapshot. Expected coverage includes truth table tests for boolean parsing; numeric validator bounds and error messages; `"auto"` handling; percentage conversion; request-node-count closures; fallocate byte/percent parsing; reseller-prefix empty-prefix and override behavior; affinity key ordering and locality predicate validation; `readconf()` file, directory, file-like, raw, missing-section, missing-file, and interpolation cases; and `parse_prefixed_conf()` section filtering.
