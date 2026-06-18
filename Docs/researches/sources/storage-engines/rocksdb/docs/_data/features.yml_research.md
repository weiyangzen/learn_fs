## sources/storage-engines/rocksdb/docs/_data/features.yml

### Purpose

`docs/_data/features.yml` defines homepage or marketing feature blocks for the RocksDB site. It lists four feature cards: high performance, optimized fast storage, adaptability, and basic/advanced operations.

### Important APIs, Types, And Functions

This is a YAML sequence of objects with `title`, block-scalar `text`, and `image`. The images point to `images/promo-performance.svg`, `images/promo-flash.svg`, `images/promo-adapt.svg`, and `images/promo-operations.svg`. The text includes Markdown links for MyRocks and a Netflix technical blog.

### Control Flow

Jekyll loads the sequence as `site.data.features`. A layout or include iterates over the entries and renders image, title, and Markdown-capable text. The block-scalar indentation preserves each paragraph as multiline content.

### State And Persistence Behavior

The file has no runtime state. It controls generated homepage/documentation feature content and depends on the referenced SVG assets being present and correctly linked relative to the generated page.

### Dependencies And Integration Points

It integrates with the site's homepage include/layout, Markdown rendering, and static image asset paths. External links introduce dependencies on GitHub and Netflix URLs for rendered content.

### Risks And Edge Cases

- If the rendering template does not pass `text` through Markdown, the embedded links will display as raw Markdown.
- Relative image paths depend on where the include is rendered; templates should use `relative_url` or a known asset base.
- Marketing text can become stale relative to supported features or external project locations.

### Test Signals

Render the homepage and inspect feature ordering, image loading, Markdown link conversion, and responsive layout with the longest text entry. Static research only; no Jekyll command was run.
