# sources/test-tools/syzkaller/pkg/html/pages/pages.go

## Purpose
`pages.go` builds self-contained HTML templates by embedding shared CSS and JavaScript into a reusable head template.

## Important APIs, Types, And Functions
`Create(page string)` replaces the first `{{HEAD}}` placeholder with the generated head block and parses the page using `html.Funcs`. `CreateFromFS(fs, patterns...)` creates a base template named `syz-head` from the embedded head block and parses template files from an `fs.FS`. `getHeadTemplate` formats embedded `style.css` and `common.js` into `<style>` and `<script>` tags. `style` and `js` are populated by `go:embed`.

## Control Flow
For string templates, `Create` performs a single placeholder replacement before parsing. For filesystem templates, `CreateFromFS` first parses the head template, then parses all requested patterns into the same template set. Both paths panic on parse errors through `template.Must`.

## State And Persistence Behavior
The embedded CSS and JS are compile-time assets. Template creation is in-memory and has no persistence. The returned templates can later execute with caller-provided data.

## Dependencies And Integration Points
The file depends on Go embedding, `html/template`, `io/fs`, and `pkg/html` for shared template functions. It integrates directly with page-specific files such as `stats.go`, which calls `Create` for an embedded template.

## Risks And Edge Cases
`Create` replaces only the first `{{HEAD}}`; missing placeholders still produce a valid template without the shared head. Embedding raw CSS and JS means any syntax or escaping problem affects every generated page. Parse failures panic, which is suitable for static templates but requires tests to catch bad template edits.

## Test Signals
`stats_test.go` indirectly confirms that `Create` can parse the embedded stats template with shared head assets. Additional tests could verify `CreateFromFS`, missing or repeated head placeholders, and helper availability.
