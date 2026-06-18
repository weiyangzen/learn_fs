# sources/object-store/openstack-swift/swift/common/middleware/x_profile/html_viewer.py

## Purpose
`html_viewer.py` is the presentation and export layer for Swift's development-only profiling middleware. It turns profile dumps collected by `ProfileLog` into an HTML form, HTML statistics table, raw profile output, JSON, CSV, ODS, source-code snippets, and optional matplotlib plots. It does not collect profiles itself; it sits behind `ProfileMiddleware` and delegates profile parsing and serialization to `Stats2`.

## Important APIs, types, and functions
The main type is `HTMLViewer(app_path, profile_module, profile_log)`. `render()` routes profiling UI/API requests based on WSGI method and `path_entry`: index requests, downloads, plots, clearing profiles, listing profile IDs, and per-function downloads. `index_page()` builds the HTML form and stats table. `download()` serializes profile data to `default`, `json`, `csv`, `ods`, or `python` source-view formats. `plot()` renders bar or pie charts from selected profile metrics. `format_source_code()` returns escaped source HTML for a `filename:lineno(function)` selector. `generate_stats_html()` emits the profile statistics table and links to per-function JSON and source views. Module templates define select boxes, form fields, and page layout; `format_dict` maps export formats to content types.

## Control flow and state behavior
`render()` normalizes query parameters with `_get_param()`, determines whether the action is `plot`, `download`, or `clear`, then resolves profile log files via `profile_log.get_logfiles()`. `/__profile__` GET/POST requests render a page or perform a form action. `/__profile__/...` GET requests either list profile IDs as JSON or download a selected profile/function. Clearing a profile calls `profile_log.clear()` and then the middleware-provided callback to renew the profiler.

The module has little durable state of its own. Persistent state is profile files on disk, owned by `ProfileLog`. Temporary state includes in-memory `Stats2` instances and, for plots, a temporary file used by matplotlib. Source-code formatting reads arbitrary `.py` files referenced by profile data and returns escaped HTML.

## Dependencies and integration points
It imports profile exceptions, `Stats2`, `html`, `os`, `re`, `string.Template`, `tempfile`, and optional `matplotlib`. It is constructed by `swift.common.middleware.xprofile.ProfileMiddleware` with the configured profile path, profiler module name, and shared `ProfileLog`. `Stats2` handles profile loading and output serialization. `ODFLIBNotInstalled`, `PLOTLIBNotInstalled`, `DataLoadFailure`, `NotFoundException`, `MethodNotAllowed`, and `ProfileException` become HTTP responses in the middleware.

## Risks and edge cases
The source-code view explicitly notes a security weakness: `format_source_code()` opens a profile-derived path if it ends in `.py`, so path disclosure/read risk depends on profile contents and local filesystem visibility. HTML generation mostly escapes function/source labels but template option values and filters should be treated carefully. Plot responses declare `image/jpg` while saving PNG bytes. `download()` wraps broad exceptions in `ProfileException`, which may obscure specific failures. `render()` appends CORS headers to direct GET downloads, exposing profile data to any origin. Missing optional dependencies disable plot or ODS export. Invalid `output_format` values can raise when indexing `format_dict`.

## Test signals
Useful tests should cover routing for index, profile-list JSON, direct download, per-function filters, clear callbacks, unsupported methods, missing log files, bad profile data, and optional dependency failures. Rendering tests should assert HTML escaping for function/source strings, selected option preservation, and source-code formatting behavior for invalid paths, non-Python files, missing files, and valid highlighted lines.
