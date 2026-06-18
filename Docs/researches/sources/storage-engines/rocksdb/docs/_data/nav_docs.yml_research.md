## sources/storage-engines/rocksdb/docs/_data/nav_docs.yml

### Purpose

`docs/_data/nav_docs.yml` defines a small documentation-side navigation tree. At this revision it contains one visible section, `Quick Start`, with one item ID, `getting-started`.

### Important APIs, Types, And Functions

The YAML sequence contains `title: Quick Start`, `items`, and an item with `id: getting-started`. The ID likely maps to a document in the Jekyll `docs` collection.

### Control Flow

Jekyll loads this as `site.data.nav_docs`. Documentation layouts can iterate sections, look up docs by `id`, and render the docs sidebar in the order declared here.

### State And Persistence Behavior

This is static navigation metadata. Adding entries affects sidebar structure and discoverability; no runtime state is changed.

### Dependencies And Integration Points

It integrates with `_docs/getting-started.*` or equivalent document metadata and with docs layouts that resolve IDs to pages. It also depends on `_config.yml` declaring the `docs` collection with output enabled.

### Risks And Edge Cases

- The file is intentionally sparse and has comments saying to fill in later, so many docs may be unreachable from the docs sidebar.
- If the `getting-started` document ID changes, the sidebar can render a dead or missing link depending on template robustness.

### Test Signals

Build docs pages and verify the sidebar resolves `getting-started` to the correct permalink. Static research only; no Jekyll command was run.
