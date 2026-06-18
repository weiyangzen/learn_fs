# sources/test-tools/syzkaller/pkg/html/pages/common.js

## Purpose
`common.js` supplies client-side behaviors embedded into syzkaller HTML pages: sortable tables, dynamic repeated input groups, collapsible sections, and AI/manual workflow form visibility.

## Important APIs, Types, And Functions
Sorting helpers include `sortTable`, `findColumnByName`, `isSorted`, and converters `textSort`, `numSort`, `floatSort`, `reproSort`, `patchedSort`, `lineSort`, and `timeSort`. Form helpers include `findAncestorByClass`, `deleteInputGroup`, `addInputGroup`, `displayAICreateJobArgs`, and `showManualWorkflowFields`. DOM event handlers are registered for `DOMContentLoaded` collapsible clicks and `load` initialization.

## Control Flow
`sortTable` climbs from the clicked element to the containing table, finds the named header column, extracts text or `sort-value` attributes from body rows, converts values, toggles sort direction based on current ordering, sorts rows, and appends them back to the table body. Input group deletion clears the only remaining group or removes the selected group; addition clones the last group and clears its input. Collapsible handling delegates clicks and toggles show/hide classes when the header is clicked. AI job helpers show or hide base-commit and workflow-specific fields while disabling inputs in hidden groups.

## State And Persistence Behavior
State is entirely in the browser DOM: row order, class lists, input values, inline `style.display`, and input disabled flags. There is no local storage or network access.

## Dependencies And Integration Points
The script is embedded by `pkg/html/pages/pages.go` into dashboard pages. It assumes table header text matches sort calls, forms use classes such as `input-group`, `input-values`, `collapsible`, and `manual-workflow-fields`, and workflow field containers use IDs derived from workflow names.

## Risks And Edge Cases
Many variables are assigned without `let` or `var`, creating globals and possible collisions. `sortTable` depends on a fixed ancestor depth and may break if markup changes. Numeric converters return `NaN` for empty or malformed values except where special cases are handled. `findAncestorByClass` returns `null` if no ancestor matches, and callers do not always guard every subsequent use. Dynamic IDs built from workflow names require safe name characters.

## Test Signals
There are no JS tests in this source set. Practical coverage would use browser or DOM tests for table sort direction toggling, form clone/delete behavior, collapsible event delegation, and workflow field enable/disable transitions.
