# sources/storage-engines/tikv/components/in_memory_engine/src/region_label.rs

## Purpose

This file watches PD region-label rules and keeps an in-memory rule map used to identify key ranges that should always be cached by the in-memory engine. It models the subset of PD label-rule JSON relevant to key-range cache labels.

## Important APIs, Types, And Functions

- `RegionLabel`, `LabelRule`, and `KeyRangeRule` mirror PD labeler JSON structures.
- `TryFrom<&KeyRangeRule> for CacheRegion` decodes TiDB hex keys and converts them to data-key/data-end-key cache ranges.
- `RegionLabelRulesManager` stores rules in a `DashMap` and invokes an optional change callback on add/remove.
- `RegionLabelServiceBuilder` wires a manager, PD RPC client, optional rule filter, and cluster id.
- `RegionLabelService::watch_region_labels` loads all rules, then watches PD meta storage for put/delete events.
- `reload_all_region_labels` performs a full prefixed get with retry.

## Control Flow

The service computes a PD meta-storage path from cluster id and `REGION_LABEL_PATH_PREFIX`. Startup calls `reload_all_region_labels`, parsing each JSON value as a `LabelRule` and applying the optional filter before adding it. The watch loop opens a prefixed watch from the last revision with previous KV data. Put events parse the new value and call `on_label_rule_add`; delete events parse `prev_kv` and call `on_label_rule_delete`. Data compaction triggers a full reload and watch restart. Other PD/watch errors log, wait one second through `GLOBAL_TIMER_HANDLE`, abort the stream, and retry.

## State And Persistence Behavior

Local state is the manager's in-memory `DashMap` plus the service's current watch revision. Durable rule storage is external PD meta storage. Duplicate identical put events are detected and ignored for callback purposes, but remove events always call the callback if configured.

## Dependencies And Integration Points

The file depends on `pd_client` meta-storage APIs, `kvproto::meta_storagepb::EventEventType`, `dashmap`, `serde_json`, `futures`, `keys::{data_key, data_end_key}`, `engine_traits::CacheRegion`, and TiKV logging/timer utilities. The callback is the integration hook for cache load/evict policy when labels change.

## Risks And Edge Cases

Invalid hex in `KeyRangeRule` or malformed JSON prevents conversion/application and only logs parse errors in watch/reload paths. The service loops forever and relies on task cancellation by its owner. Watch revision handling uses response-header revisions; compaction is handled, but missed deletes before reload could leave stale local rules until the full reload completes. `path_suffix` exists but is only internally set to `None` by the builder in this file.

## Test Signals

Tests include a disabled local PD debugging test and mock-PD CRUD/watch tests. Helpers create label rules, insert/delete through PD meta storage, and assert the manager observes additions and removals.
