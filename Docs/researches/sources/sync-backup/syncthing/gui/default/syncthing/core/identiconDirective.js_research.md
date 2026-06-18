# sources/sync-backup/syncthing/gui/default/syncthing/core/identiconDirective.js

## Purpose
This directive renders a deterministic SVG identicon for a supplied value, typically a device ID or other stable identifier shown in the Syncthing GUI.

## Important APIs, types, and functions
It registers an element directive `identicon` with isolate scope `{ value: '=' }`. The inner `Identicon(value, size)` function creates an SVG in the SVG namespace, defaults to a 5x5 grid, and fills mirrored rectangles based on the parity of character codes from the sanitized value.

## Control flow
The directive link function appends a newly constructed `Identicon(scope.value)` to the element once. `Identicon` removes non-word and underscore characters from the value, iterates rows and the left/middle columns, fills a rectangle when `value.charCodeAt(row + col * size)` is even, and mirrors filled rectangles across the vertical axis except for the center column in odd-size grids.

## State and persistence behavior
The directive is stateless after initial render and does not watch `value` for later changes. It does not persist data.

## Dependencies and integration points
Dependencies are AngularJS, the browser DOM/SVG APIs, and `$window.parseInt`. CSS class `identicon` controls visual styling such as fill color. Templates use `<identicon value="...">` where the value is expected to be stable before linking.

## Risks
If `value` changes after link, the SVG remains stale. For short sanitized values, `charCodeAt` can return `NaN`, and `$window.parseInt(NaN, 10) % 2` leads to no fill for those cells. Identicons are not cryptographic; collisions and visually sparse icons are possible. Appending directly without clearing can duplicate SVGs if the directive is re-linked on reused DOM.

## Test signals
Tests should render known values and assert deterministic SVG rectangle positions, symmetry, empty-value behavior, and non-updating behavior when scope value changes. Visual smoke tests should confirm CSS makes the generated SVG visible at intended sizes.
