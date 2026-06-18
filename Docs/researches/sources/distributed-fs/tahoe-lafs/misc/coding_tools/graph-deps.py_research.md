# sources/distributed-fs/tahoe-lafs/misc/coding_tools/graph-deps.py

## Purpose

This dependency visualization tool builds or loads wheels for a target package, parses wheel metadata for runtime requirements and extras, emits a Graphviz DOT dependency graph, and renders it to `out.png`.

## Important APIs, Types, and Functions

`build_wheels` runs `pip wheel` and infers a root package name. `parse_metadata_json`, `parse_METADATA`, and `parse_wheels` populate global `all_packages`, `all_reqs`, and `all_pure`. `parse_spec` splits requirement strings into package, extras, and constraints. `scan` recursively marks base and extra dependency nodes. `generate_dot` writes package/extra nodes and colored edges. `dot_to_png` invokes `dot`. The Click command `go` coordinates all phases.

## Control Flow

If `--wheeldir` is an existing directory, wheels are reused; if it names a missing path, wheels are built there; otherwise a temporary directory is used. After metadata parsing, all base package nodes are shown, the root dependency tree is recursively scanned including requested extras, DOT is optionally written to `out.dot`, and Graphviz renders `out.png`.

## State, Dependencies, Integration, Risks, and Tests

Persistent state may include wheel dirs, `root_pkgname`, `out.dot`, and `out.png`. Dependencies are `pip`, wheel metadata formats, Click, and Graphviz. Risks include fragile root-name inference from pip output, global mutable state across invocations, incomplete PEP 508 marker parsing, recursion KeyErrors for missing dependency wheels, and unclosed zip files. Tests should use synthetic wheels with METADATA and metadata.json, extras, pure/non-pure WHEEL records, missing metadata, and DOT snapshot checks.
