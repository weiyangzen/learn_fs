## sources/storage-engines/rocksdb/docs/_config.yml

### Purpose

`docs/_config.yml` is the Jekyll site configuration for the RocksDB documentation and blog. It defines site identity, URLs, repository metadata, theme colors, collections, Markdown/highlighting behavior, plugins, and legacy author metadata embedded directly in the config.

### Important APIs, Types, And Functions

This is declarative YAML rather than executable code. Important keys include `permalink`, `title`, `tagline`, `description`, `fbappid`, `gacode`, `baseurl`, `url`, `ghrepo`, `color`, `collections`, `markdown`, `kramdown`, `sass`, `redcarpet`, `plugins`, and author-id mappings such as `icanadi`, `siying`, `pdillinger`, and others.

### Control Flow

Jekyll loads this file before rendering the site. Collection declarations make `_docs` render under `/docs/:name/` and `_top-level` render as top-level HTML pages. Markdown is processed through kramdown with GitHub-flavored input and Rouge highlighting. The `jekyll-redirect-from` plugin is enabled. Liquid templates can access all top-level keys through `site.*`.

### State And Persistence Behavior

The file persists site-wide build state in source control. It does not mutate runtime data, but a change to `baseurl`, `url`, collection permalinks, or Markdown/highlighter settings changes generated page paths, feed links, canonical URLs, and rendered code blocks.

### Dependencies And Integration Points

It integrates with Jekyll, kramdown, Rouge, Sass, `jekyll-redirect-from`, GitHub Pages conventions, and site templates under the docs tree. The `ghrepo` value points navigation or template helpers at `facebook/rocksdb`. Author metadata can be consumed by posts or layouts that look up `site.<author_id>`.

### Risks And Edge Cases

- `url` uses `http://rocksdb.org`, while feed.xml hardcodes an HTTPS link; mixed absolute URL settings can create inconsistent canonical/feed URLs.
- The config has comments about Jekyll 3.3 absolute/relative URL behavior, so older template assumptions may break if `baseurl` changes.
- Author data appears duplicated with `_data/authors.yml`; divergent names or IDs could confuse layouts depending on which data source they use.
- `redcarpet` settings remain even though `markdown: kramdown`; this is harmless for current Jekyll but can mislead maintainers.

### Test Signals

Run a Jekyll build and inspect generated docs, top-level pages, syntax highlighting classes, redirects, RSS absolute URLs, and author rendering. Static research only; no Jekyll command was run.
