# sources/storage-engines/wiredtiger/src/config/config_collapse.c

## Purpose

`config_collapse.c` builds canonical configuration strings from ordered config layers. It has two related but distinct behaviors. `__wt_config_collapse` performs a shallow collapse using the first config string as the key universe and later strings as overrides. `__wt_config_merge` performs a deeper merge by flattening nested named structures, sorting all discovered entries, selecting the last value for each key, optionally stripping selected values, and reconstructing a nested config string.

These helpers are used when WiredTiger needs a newly allocated configuration string for metadata, schema, connection, tiered-storage, and utility paths.

## Important APIs, Types, and Functions

`__wt_config_collapse(WT_SESSION_IMPL *, const char **cfg, char **config_ret)` walks only `cfg[0]`, resolves each key’s final value across the full NULL-terminated config stack with `__wti_config_get`, appends `key=value,` into a scratch buffer, strips the trailing comma, and returns an allocated copy.

`WT_CONFIG_MERGE_ENTRY` stores one flattened key/value pair: duplicated key string, duplicated value string, generation number, and `strip` flag. The generation makes sorting stable for identical keys so later config layers win.

`WT_CONFIG_MERGE` owns the dynamically grown array of merge entries.

`__config_merge_scan` parses one config string, preserves quotes for string keys and values, rejects keys containing the separator character `[`, flattens nested named structures using separator-delimited key paths, detects whether struct values should be recursively merged, and appends scalar or unmergeable entries to the merge array.

`__config_merge_format_next` recursively reconstructs a config string from the sorted flattened entries. It skips superseded entries, treats nested keys as substructures, discards empty stripped levels, skips entries marked `strip`, and appends final `key=value,` fragments.

`__config_merge_format` allocates the output formatting buffer, starts recursive formatting at the root prefix, strips the final comma, and duplicates the result.

`__config_merge_cmp` sorts entries by flattened key and then generation.

`__wt_config_tiered_strip` is a convenience wrapper that strips `tiered_storage=(shared=)` from the merged output before metadata persistence.

`__wt_config_merge(WT_SESSION_IMPL *, const char **cfg, const char *cfg_strip, const char **config_ret)` is the exported deep merge entry point. It scans all config strings in least-to-most-preferred order, scans optional strip config last with `strip=true`, sorts, formats, frees the temporary entries, and returns the allocated merged config string.

## Control Flow

`__wt_config_collapse` starts with `*config_ret = NULL`, allocates a scratch buffer, initializes a parser over the first/default config string, and loops through default keys. For each key it validates the key token type, asks `__wti_config_get` for the effective value across all config strings, extends string keys and values to include surrounding quotes when present, and appends a comma-delimited assignment. The expected parser termination is `WT_NOTFOUND`; any other parser result is returned. The function handles an empty default config by returning an allocated empty string.

`__config_merge_scan` is the input flattening phase for deep merge. It parses one config string, creates scratch key and value buffers, and for each item constructs a flattened key as either `key` or `parent[key`. If the value is a struct, it recurses only when the struct has named fields, detected by `=` in the value, or when a previous flattened entry proves the same key has been a struct before. This second rule handles cases such as `log=(enabled)` overriding a previous named struct. Unnamed structs such as checkpoint LSN tuples are treated as scalar values and not decomposed.

`__wt_config_merge` scans normal config layers first and a strip layer last. Because every inserted entry gets a monotonically increasing generation, the final sort by key/generation places strip requests and later overrides after earlier defaults for the same flattened key.

`__config_merge_format_next` walks sorted entries. It skips earlier identical keys and earlier scalar entries replaced by later nested keys. When the next separator introduces a nested level, it appends `name=(`, recurses with the nested prefix, strips the nested trailing comma, appends `),`, and then removes the entire level if recursion produced an empty `()`. It skips entries marked for stripping and appends remaining scalar entries using the suffix after the current prefix.

## State and Persistence Behavior

All outputs are newly allocated strings owned by the caller. Temporary scratch buffers and merge arrays are freed before return. The functions do not mutate connection-global state.

The output strings often become persisted metadata or connection configuration state through callers. Integration searches show collapse/merge usage in metadata checkpoint updates, cursor metadata reads, schema create/alter, import, connection dhandle setup, connection reconfigure/open, tiered handle logic, compact config stripping, and `wt load`.

`__wt_config_tiered_strip` is explicitly persistence-oriented: it removes tiered storage fields that should not be stored in metadata, currently `tiered_storage=(shared=)`.

Ordering is canonicalized differently by the two APIs. Collapse preserves the order of keys in the first config string and drops any keys absent from that first string. Merge sorts flattened keys lexicographically before formatting, so output order is deterministic but not input-order preserving.

## Dependencies and Integration Points

This file depends on parser helpers (`__wt_config_init`, `__wt_config_next`, `__wti_config_get`), scratch buffers (`__wt_scr_alloc`, `__wt_scr_free`), dynamic buffers (`__wt_buf_fmt`, `__wt_buf_catfmt`), allocation helpers (`__wt_realloc_def`, `__wt_strndup`, `__wt_free`), `__wt_qsort`, and `WT_CONFIG_PRESERVE_QUOTES`.

Public declarations are in `src/include/extern.h`, with `__wt_config_merge` exported with default visibility. The export is used outside the immediate config module, including utilities and tiered/schema/connection code.

The behavior depends on tokenizer details from `config.h`: string item pointers can be expanded one byte backward and one byte forward by `WT_CONFIG_PRESERVE_QUOTES` when the original token was quoted.

Callers include `meta_ckpt.c`, `cur_metadata.c`, `schema_create.c`, `schema_alter.c`, `bt_import.c`, `conn_dhandle.c`, `conn_tiered.c`, `conn_reconfig.c`, `conn_api.c`, `conn_compact.c`, `tiered_handle.c`, and `utilities/util_load.c`.

## Risks and Edge Cases

`__wt_config_collapse` never emits keys that are absent from `cfg[0]`. That is intentional for default-driven collapse but dangerous if callers expect later config strings to introduce new keys.

Collapse does not merge nested structures. A later `key=(k4=v4)` replaces an earlier `key=(k2=v2,k3=v3)` as a whole.

Merge uses `[` as an internal separator and rejects source keys containing it. The comment notes this is not completely safe because JSON quoting could allow literal separator characters in application-controlled key namespaces.

The heuristic for deciding whether a struct is mergeable depends on `=` in the value or prior entries with the same prefix. This preserves unnamed tuple structs, but ambiguous values can behave differently depending on earlier config layers.

`__config_merge_format_next` relies on sorted flattened key order and separator placement to recurse correctly. Changes to the separator, sort comparator, or key construction must be coordinated.

Strip behavior is generation-based. Strip configs are scanned last so they override previous values; scanning strips earlier would silently fail to remove later values.

`__config_merge_cmp` returns only `1` or `-1` for equal keys based on generation and never returns `0` for two entries with the same key/generation. Since generation is unique per inserted entry this is stable enough, but duplicate generation bugs would violate comparator expectations.

Both APIs preserve quotes by adjusting parsed item spans. This assumes parser-provided string pointers have valid adjacent quote bytes as documented by `WT_CONFIG_PRESERVE_QUOTES`.

Error messages for invalid key types use `%s` with `k.str` in this file, while parsed keys are length-delimited. If malformed input produces a non-NUL-terminated key span for that error path, diagnostics may read past the token.

## Test Signals

Useful existing signals come from schema/metadata/tiered/connection tests that compare persisted metadata strings and from `test/csuite/config/main.c`, which recursively validates parser-visible merged configuration results against ordered inputs.

Targeted tests should cover collapse preserving first-config key order and dropping later-only keys, collapse replacing nested structs wholesale, merge combining named nested fields, merge preserving unnamed structs such as `(1,0)`, override precedence across multiple layers, scalar-to-struct and struct-to-scalar replacement, quote preservation for string keys and values, strip removal of scalar and nested keys, empty nested levels being removed after strip, separator-character rejection, and tiered-storage strip behavior for metadata-safe output.
