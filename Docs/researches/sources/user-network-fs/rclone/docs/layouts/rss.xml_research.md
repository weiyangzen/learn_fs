<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/layouts/rss.xml -->
# sources/user-network-fs/rclone/docs/layouts/rss.xml

## Purpose

`rss.xml` is the Hugo RSS feed template for rclone documentation pages.

## Important APIs, Types, and Functions

It emits RSS 2.0 with Atom namespace, site/page title, permalink, language, author, rights, updated timestamp, and the first 15 pages as feed items containing title, link, pubDate, author, guid, and HTML-rendered content.

## Control Flow

Hugo evaluates `.Data.Pages`, formats dates with RFC-like layout, and serializes `.Content | html` into item descriptions.

## State and Persistence Behavior

No state is stored. Feed content is generated from site pages during build.

## Dependencies and Integration Points

It integrates with Hugo page collections, site metadata, and feed consumers.

## Risks and Test Signals

Risks include invalid XML from unescaped content, stale author/rights metadata, and overly large descriptions. Tests should validate generated RSS XML and feed item ordering/count.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/layouts/rss.xml -->
