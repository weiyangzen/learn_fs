# sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/js/ozonedoc.js

## Purpose
This small custom theme script applies Bootstrap table styling to all tables in generated Ozone documentation pages.

## Important functions and APIs
- Uses jQuery's document-ready shorthand: `$(function(){ ... })`.
- Selects all `table` elements.
- Calls `.addClass("table table-condensed table-bordered table-striped")`.

## Control flow
When the DOM is ready, the callback runs once, finds every table in the document, and adds Bootstrap 3 classes. This makes Markdown-generated tables adopt Bootstrap's table styling without requiring authors to add classes manually.

## State and persistence
The only state change is DOM mutation in the current page: class names are added to table elements. There is no persistent storage and no network activity.

## Dependencies and integration points
This depends on jQuery and Bootstrap CSS. It complements `jquery-3.5.1.min.js` and `bootstrap.min.js` in the `ozonedoc` theme. It integrates with Hugo-rendered Markdown content because Markdown tables become plain HTML `table` elements.

## Risks and edge cases
- It styles every table globally, including any table-like layout or third-party widget that may not be intended to use Bootstrap table classes.
- If jQuery fails to load, this script fails because `$` is undefined.
- It does not handle tables inserted after DOM ready; dynamically added content would need another call or delegated handling.
- The script assumes Bootstrap 3 class names; Bootstrap major-version upgrades may require different class choices.

## Test signals
Build a docs page with a Markdown table and confirm the generated table has `table`, `table-condensed`, `table-bordered`, and `table-striped` classes after page load. Also verify no console error occurs when scripts load in theme order.
