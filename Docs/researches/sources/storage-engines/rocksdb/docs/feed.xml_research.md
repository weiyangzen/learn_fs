## sources/storage-engines/rocksdb/docs/feed.xml

### Purpose

`docs/feed.xml` is a Jekyll/Liquid RSS 2.0 template for the RocksDB blog feed. It renders site metadata and the ten most recent posts into XML.

### Important APIs, Types, And Functions

The file has front matter `layout: null`, then emits RSS XML with Liquid variables and filters: `site.title`, `site.description`, `site.time`, `jekyll.version`, `site.posts limit:10`, `post.title`, `post.content`, `post.date`, `post.url`, `post.tags`, `post.categories`, `xml_escape`, `absolute_url`, and `date_to_rfc822`.

### Control Flow

Jekyll treats the file as a template because of the front matter. During build, Liquid renders channel metadata, then loops over at most ten posts and emits an `<item>` for each. Tags and categories are emitted as repeated `<category>` elements.

### State And Persistence Behavior

The generated feed changes with site build time and post content. It is otherwise stateless. `pubDate` and `lastBuildDate` use `site.time`, so they update on each build even when posts do not change.

### Dependencies And Integration Points

It depends on `_config.yml` values, Jekyll post collection state, Liquid filters, and the configured `url`/`baseurl` behavior used by `absolute_url`. It hardcodes the channel `<link>` to `https://rocksdb.org/feed.xml`.

### Risks And Edge Cases

- Full `post.content` is embedded in descriptions, which can make feed items large and can include escaped HTML rather than summaries.
- The channel link is HTTPS while `_config.yml` sets `url` to HTTP; consumers can see inconsistent feed and item URL schemes.
- A `site.posts limit:10` feed omits older posts without pagination.
- XML validity depends on consistent use of `xml_escape`; custom post content should be checked for escaped output size and readability.

### Test Signals

Run a Jekyll build, validate the generated feed with an RSS/XML validator, inspect absolute URLs, and check posts with tags/categories and HTML-heavy content. Static research only; no Jekyll command was run.
