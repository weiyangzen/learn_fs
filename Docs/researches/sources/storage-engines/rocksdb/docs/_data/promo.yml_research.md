## sources/storage-engines/rocksdb/docs/_data/promo.yml

### Purpose

`docs/_data/promo.yml` defines promotional controls for the RocksDB homepage header. At this revision it contains a single button linking users to getting-started documentation.

### Important APIs, Types, And Functions

The YAML sequence has one object with `type: button`, `href: docs/getting-started.html`, and `text: Get Started`.

### Control Flow

Jekyll loads this as `site.data.promo`. A homepage/header template can iterate the promo entries and render controls based on `type`.

### State And Persistence Behavior

This file controls generated static markup only. Changing `href` or `text` changes the rendered call-to-action but not runtime state.

### Dependencies And Integration Points

It depends on a generated getting-started page at `docs/getting-started.html` or equivalent redirect behavior. It also depends on template logic that maps `type: button` to button styling and link semantics.

### Risks And Edge Cases

- The href lacks a leading slash and is not explicitly passed through `relative_url`; rendering location can affect the resolved link if templates do not normalize it.
- The target format differs from the `_config.yml` docs collection permalink pattern `/docs/:name/`, so generated sites may need redirects or legacy path support.

### Test Signals

Render the homepage and verify the button points to an existing getting-started page under both local and production base URLs. Static research only; no Jekyll command was run.
