## sources/storage-engines/rocksdb/docs/_data/nav.yml

### Purpose

`docs/_data/nav.yml` defines the primary RocksDB site navigation. It mixes internal documentation/support/blog links and external links to GitHub, API source trees, and Facebook.

### Important APIs, Types, And Functions

This YAML sequence uses `title`, `href`, and `category`. Categories include `docs`, `external`, `support`, and `blog`. Entries include Docs, GitHub, API (C++), API (Java), Support, Blog, and Facebook.

### Control Flow

Jekyll loads the sequence as `site.data.nav`. Navigation templates can iterate over entries, treat `category: external` specially, and prepend or avoid `site.baseurl`/`site.url` based on category. The comments explicitly document the external-link behavior.

### State And Persistence Behavior

The file persists navigation structure in source control. Changes affect every page that renders the shared nav but do not mutate runtime state.

### Dependencies And Integration Points

It depends on templates that understand `category` semantics. Internal hrefs integrate with the configured collections and top-level support/blog pages. External API links point at RocksDB source paths under GitHub.

### Risks And Edge Cases

- External source links use GitHub `main`, so rendered docs can point at APIs that differ from the checked-out documentation version.
- Internal links are absolute from site root and must be combined correctly with `baseurl` if the site is hosted under a subpath.
- New categories require template support; otherwise styling or URL handling can be wrong.

### Test Signals

Build the site with `baseurl` empty and non-empty, inspect nav hrefs, and verify external links are not rewritten as site-relative links. Static research only; no Jekyll command was run.
