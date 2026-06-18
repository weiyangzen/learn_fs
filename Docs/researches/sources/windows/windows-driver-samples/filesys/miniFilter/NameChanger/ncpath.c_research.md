# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncpath.c

## Purpose

`ncpath.c` is the core path comparison and construction module for NameChanger. It determines how a candidate name overlaps a mapping and constructs rewritten paths from a mapping plus remainder.

## Functions

- `NcComparePath` compares an input name against a mapping entry’s long and short paths. It can compare full device-qualified paths or volume-relative paths. It classifies overlap into flags such as `InMapping`, `Match`, `Peer`, `Parent`, and `Ancestor`, and optionally returns the unmatched remainder after the mapping.
- The comparison is component-based, honors case sensitivity, treats `\` and `:` as terminators for input components, compares both long and short mapping components in parallel, and uses component counts from `NC_MAPPING_PATH` to decide final relationship.
- `NcConstructPath` builds a new path from a mapping entry and a remainder. It can include or omit the volume prefix, inserts a separator only when the remainder is non-empty, checks the `MAXUSHORT` `UNICODE_STRING` limit, and allocates the result from paged pool with `NC_GENERATE_NAME_TAG`.
- `NcParseFinalComponent` splits a configured volume-relative absolute path into parent path and final component. It keeps root parent paths as `\`, rejects paths without separators or with empty final components, and allocates both returned strings from nonpaged pool.

## Integration

Nearly every NameChanger behavior depends on this file: create redirection, name generation, directory enumeration, notifications, hard links, renames, set-link operations, and FSCTL result rewriting.

## Risks and Notes

`NcComparePath` is intentionally semantic rather than a simple prefix check. Its correctness depends on valid mapping component counts and on callers choosing the correct `ContainsDevice` setting. `NcConstructPath` may make otherwise valid on-disk names inaccessible if mapping expansion pushes the generated path beyond `UNICODE_STRING` length limits.
