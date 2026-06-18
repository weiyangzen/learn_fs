# sources/sync-backup/syncthing/gui/default/syncthing/core/metricFilter.js

## Purpose
This AngularJS filter formats numeric quantities with decimal metric prefixes for GUI display.

## Important APIs, types, and functions
It registers `metric` on `syncthing.core`. The filter delegates to global `unitPrefixed(input, false)`, using a factor of 1000 and suffixes such as `k`, `M`, `G`, and `T`.

## Control flow
The filter has no local branching. All threshold and locale-aware formatting logic resides in `app.js`'s `unitPrefixed`.

## State and persistence behavior
The filter is stateless.

## Dependencies and integration points
It requires `unitPrefixed` in global scope and Angular module initialization. Templates use it for rates or counts where decimal SI-style formatting is desired.

## Risks
Load-order coupling to a global helper is implicit. Undefined or invalid values become `'0 '`, and the filter returns a prefix-bearing number without the base unit. Very large values are expressed as large tera values because no peta prefix is implemented.

## Test signals
Cover threshold boundaries around 1000, 1e6, 1e9, 1e12, undefined, `NaN`, and locale effects. Template smoke tests should confirm surrounding unit text is correct.
