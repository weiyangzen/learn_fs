# sources/object-store/rustfs/crates/protocols/src/swift/staticweb.rs

Implements Swift container static website behavior. Container metadata configures index documents, error documents, optional directory listings, and listing CSS.

Important API surface: `StaticWebConfig` holds `index`, `error`, `listings`, and `listings_css`, with accessors. `load_config()` reads container metadata keys `web-index`, `web-error`, `web-listings`, and `web-listings-css`. `is_enabled()` checks whether an index document is configured. Pure helpers include `detect_content_type`, `normalize_path`, `is_directory_path`, `resolve_path`, breadcrumb generation, and `generate_directory_listing`. `handle_static_web_get()` is the request handler.

Control flow: the handler loads config, rejects disabled containers, resolves the incoming path, and either generates a listing or attempts to serve an object. Listing mode uses `container::list_objects` with an optional prefix and returns generated HTML. Object mode streams `object::get_object` through `ReaderStream`; a not-found object triggers the configured error document if present, otherwise a plain 404 response.

Persistent state is container metadata plus normal objects for pages, CSS, and error documents. The module does not mutate storage. It depends on Swift `container` and `object` modules, `Credentials`, `s3s::Body`, `axum::http::Response`, and tracing. The Swift handler calls `is_enabled` and `handle_static_web_get` before ordinary object GET behavior.

Risks: generated HTML directly interpolates object names, paths, and CSS hrefs without escaping, so listing XSS is possible. Directory-without-trailing-slash redirect behavior is documented but not implemented in this file. `is_enabled()` requires an index even if listings alone are configured, making listings-only hosting unreachable through the public check. Listing links are root-relative and may not preserve Swift prefixes.

Tests cover config accessors, MIME detection, path normalization, directory detection, path resolution, breadcrumbs, listing structure, size formatting, parent links, index/listing priority, and case-insensitive extensions.
