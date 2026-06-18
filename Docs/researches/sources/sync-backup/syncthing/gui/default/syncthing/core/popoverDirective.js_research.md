# sources/sync-backup/syncthing/gui/default/syncthing/core/popoverDirective.js

## Purpose
This directive initializes Bootstrap popovers on elements that declare the `popover` attribute.

## Important APIs, types, and functions
It registers attribute directive `popover` on `syncthing.core`. The link function calls `$(element).popover()`.

## Control flow
There is no branching. Initialization occurs once when Angular links the element.

## State and persistence behavior
The directive creates Bootstrap/jQuery plugin state attached to the DOM element. It does not persist application data and does not explicitly destroy popover state on scope teardown.

## Dependencies and integration points
Dependencies are AngularJS, jQuery, Bootstrap's popover plugin, and markup attributes consumed by Bootstrap such as title, content, placement, trigger, or data attributes. It integrates with templates that need hover/click contextual help.

## Risks
If Bootstrap's popover plugin is not loaded, `$(element).popover` is undefined. Dynamic content changes after initialization may not update unless Bootstrap is configured accordingly. Missing destroy cleanup can leave event handlers on frequently recreated elements.

## Test signals
Browser tests should confirm popovers initialize and display with expected content and placement. Unit tests can stub `$.fn.popover` and assert it is called once per linked element; teardown behavior should be considered if elements are dynamic.
