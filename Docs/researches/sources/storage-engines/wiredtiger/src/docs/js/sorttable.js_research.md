# sources/storage-engines/wiredtiger/src/docs/js/sorttable.js

## Purpose
Bundled browser-side sortable table library, modified for WiredTiger so alphabetic sorting is case-insensitive. It enables Doxygen/reference-manual HTML tables with class `sortable` to sort when a header is clicked.

## Important APIs and control flow
The global `sorttable` object exposes `init`, `makeSortable`, `guessType`, `getInnerText`, `reverse`, sort comparators, and `shaker_sort`. Initialization runs on DOM ready across modern browsers, old IE, Safari polling, and `window.onload`. `makeSortable` ensures a `thead`, moves `sortbottom` rows into `tfoot`, detects column types or explicit `sorttable_<type>` classes, attaches header click handlers, builds decorated row arrays, sorts, and appends rows back into the tbody. Repeated clicks reverse the current ordering and update sort indicators.

## State, dependencies, integration, risks
State is stored directly on DOM nodes (`sorttable_sortfunction`, column index, tbody reference, CSS classes, indicator spans) and in global helpers such as `forEach` and event handlers. It depends only on browser DOM APIs. Risks are global-variable leakage, old-browser compatibility code, non-stable default JavaScript sort, numeric/date parser ambiguity, missing cells in ragged tables, and `innerHTML` indicators. Test signals are sortable Doxygen tables with text, numeric, date, custom-key, input-containing, no-sort, sortbottom, and repeated reverse-click cases.
