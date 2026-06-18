# sources/user-network-fs/rclone/lib/http/serve/dir_test.go

Source read signal: reviewed complete local file (126 lines, sha256 724e692a573299e3).

Purpose: Unit-tests directory-listing construction, URL escaping, error responses, and template rendering.

Important APIs/types/functions: `GetTemplate`, `TestNewDirectory`, `TestSetQuery`, `TestAddHTMLEntry`, `TestAddEntry`, `TestError`, and `TestServe`.

Control flow: Tests construct directories with the golden template, add file/dir entries, assert exact `DirEntry` slices for escaped URLs/query strings, exercise `Error`, and render a listing through `httptest`.

State and persistence behavior: Reads a template from testdata; no persistent writes.

Dependencies and integration points: Uses `httptest`, `html/template`, `lib/http.GetTemplate`, `testify`, and the serve directory types.

Risks and test signals: Exact HTML output protects template data shape. Query propagation for `ZipURL` differs from entry query in the current behavior and is captured by tests.
