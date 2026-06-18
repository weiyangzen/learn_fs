# sources/test-tools/syzkaller/dashboard/app/static/coverage.js

Purpose: browser-side behavior for coverage report pages, including collapsible file-tree navigation, query-parameter-backed update form initialization, and asynchronous file coverage detail display.

Important functions: `initTogglers`, `initUpdateForm`, and `onShowFileContent`.

Control flow: document-ready handlers register click toggles on `.caret` elements and update the `#unique-only` checkbox when `#target-manager` changes. `initUpdateForm` reads current URL query parameters and pushes `period`, `period_count`, `subsystem`, `manager`, and `unique-only` into form controls. `onShowFileContent` appends selected subsystem/manager/unique-only query values to the requested detail URL, fetches HTML with jQuery, shifts current file content/details into “previous” containers, and writes the fetched response and source parameter summary into the current containers.

State and persistence: all state is DOM and URL-derived. No persistent client storage is used. The previous/current panels preserve one step of viewing history by copying HTML between `#file-content-prev`, `#file-content-curr`, `#file-details-prev`, and `#file-details-curr`.

Dependencies and integration points: depends on jQuery, coverage page markup IDs, `.caret`/`.nested` CSS classes, and server endpoints that return HTML fragments for file coverage content. It integrates with the coverage report query language by preserving subsystem, manager, and unique-only filters.

Risks: URL concatenation assumes the incoming `url` already has a query string and appends unescaped parameter values. The unique-only checkbox is disabled when manager is `*`/empty, but stale URL values can still be displayed. The HTML response is inserted directly into the page, so the endpoint must return trusted/sanitized markup.

Test signals: no direct JS test file here. Server-side `TestCoverageRegression` validates related coverage-report email generation, but interactive file-content behavior depends on browser/manual coverage.
