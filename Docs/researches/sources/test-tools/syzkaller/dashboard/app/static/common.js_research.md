# sources/test-tools/syzkaller/dashboard/app/static/common.js

Purpose: shared browser-side helpers for dashboard pages: sortable tables, dynamic repeated input groups, collapsible blocks, and conditional display of AI job form fields.

Important functions: `sortTable`, `findColumnByName`, `isSorted`, sorting converters (`textSort`, `numSort`, `floatSort`, `reproSort`, `patchedSort`, `lineSort`, `timeSort`), `findAncestorByClass`, `deleteInputGroup`, `addInputGroup`, `displayAICreateJobArgs`, and `showManualWorkflowFields`.

Control flow: `sortTable` walks from the clicked item to the containing table, finds a column by header text, extracts cell text or explicit `sort-value`, toggles ascending/descending based on current sortedness, sorts row references, and appends them back to the tbody. Input helpers clone or remove `.input-group` elements, preserving at least one blank input. DOM listeners initialize collapsible sections on `DOMContentLoaded` and AI workflow field visibility on `load`.

State and persistence: state is only DOM state. Sorting mutates row order in the current table. Collapsible sections toggle CSS classes. AI form helpers set `style.display` and `disabled` on input groups so hidden manual workflow fields are not submitted. No local storage or server persistence is used.

Dependencies and integration points: plain browser DOM APIs; expected markup includes table headers, `.input-values`, `.input-group`, `.collapsible`, `.head`, `select[name="ai-job-create"]`, `#ai-set-base-commit`, `#base_commit_custom`, `#base_commit_input`, `#ai-job-create`, and `#workflow-fields-<workflow>`.

Risks: variables are implicitly global in several functions because `let`/`const` is omitted, which can cause collisions. `sortTable` depends on a fixed DOM ancestor depth and exact header text. `timeSort` parses compact strings such as `1d2h` and falls back to a large value for unknown formats; presentation changes can alter ordering. Cloned input groups copy any extra attributes/events not reset beyond the first input value.

Test signals: no direct JS tests in this subset. Coverage is likely indirect through dashboard UI tests/manual use; regressions would show as broken table sorting, duplicate form values, or missing AI manual workflow fields.
