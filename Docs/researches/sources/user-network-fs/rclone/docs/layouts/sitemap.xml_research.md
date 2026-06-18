<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/layouts/sitemap.xml -->
# sources/user-network-fs/rclone/docs/layouts/sitemap.xml

## Purpose

`sitemap.xml` is the Hugo sitemap template for rclone.org.

## Important APIs, Types, and Functions

It emits a standard sitemap URL set, iterating `.Data.Pages` and writing location, last modification timestamp, optional change frequency, and optional priority.

## Control Flow

Hugo provides page metadata; the template formats dates as ISO-like timestamps and conditionally renders sitemap attributes.

## State and Persistence Behavior

No runtime state is stored. Output depends on page dates and sitemap metadata.

## Dependencies and Integration Points

It integrates with search engine indexing expectations and Hugo page metadata.

## Risks and Test Signals

Risks include malformed XML, missing safe escaping for URLs, and bad dates. Tests should run Hugo and validate the sitemap against XML parsing and expected URL counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/layouts/sitemap.xml -->
