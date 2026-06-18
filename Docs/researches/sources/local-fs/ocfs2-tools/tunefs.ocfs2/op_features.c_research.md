# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_features.c

## Role

Implements `--fs-features` and feature-derived options by parsing requested OCFS2 feature enables/disables, checking they are supported by this tunefs binary, and invoking feature-specific implementations.

## Feature Table

The supported tunefs feature list includes:

- backup superblocks
- extended slot map
- inline data
- local mount mode
- metaecc
- sparse files
- unwritten extents
- xattrs
- user quota
- group quota
- refcount
- indexed directories
- discontiguous block groups
- clusterinfo
- append direct I/O

Each entry is an external `struct tunefs_feature` with name, feature bitset, enable/disable handlers, action, and open flags.

## Parse Flow

`features_parse_option()` allocates `struct feature_op_state`, parses the feature string with `ocfs2_parse_feature()`, then iterates enable and disable sets.

`check_supported_func()` verifies each requested feature exists in the local table and supports the requested direction. It sets `feat->tf_action` and ORs the feature's required open flags into the parent operation.

## Run Flow

`features_run()` runs disables first via `ocfs2_feature_reverse_foreach()`, then enables via `ocfs2_feature_foreach()`. Each callback resolves the feature and calls `tunefs_feature_run()`.

The operation is declared with initial open flags `0`; required flags are accumulated dynamically during parse based on the selected features.

## Metadata Touched

This file does not directly modify filesystem metadata. Actual mutations are delegated to each `tunefs_feature` implementation.

## Notable Risks

- `struct run_features_context` has `rc_error`, but `run_feature_func()` never assigns it, and `features_run()` ignores the return values of the foreach calls. Unless the iterator itself has non-obvious side effects, callback errors may not be propagated correctly.
- Feature actions are stored in global feature descriptors. That is simple for a one-shot CLI, but it makes the design stateful and awkward for library-style reuse.
