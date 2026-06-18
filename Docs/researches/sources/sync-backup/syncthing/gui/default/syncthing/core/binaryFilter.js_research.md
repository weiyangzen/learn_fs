# sources/sync-backup/syncthing/gui/default/syncthing/core/binaryFilter.js

## Purpose
This AngularJS filter formats byte-like quantities with binary prefixes for GUI display.

## Important APIs, types, and functions
It registers the `binary` filter on `syncthing.core`. The filter delegates entirely to the global `unitPrefixed(input, true)` helper from `app.js`, which formats using a 1024 factor and suffixes binary units with `i` (`Ki`, `Mi`, `Gi`, `Ti`).

## Control flow
There is no local branching; all formatting control flow lives in `unitPrefixed`.

## State and persistence behavior
The filter is stateless.

## Dependencies and integration points
It requires `unitPrefixed` to exist in global scope before the filter is invoked. Templates likely combine it with size values for files, transfer rates, database sizes, or device statistics.

## Risks
Load-order issues break the filter at runtime because `unitPrefixed` is not injected. Undefined or non-numeric handling follows `unitPrefixed`, which returns `'0 '` for undefined or `NaN`. The filter appends only the prefix, so templates must supply the base unit such as `B` or `/s` where needed.

## Test signals
Check threshold values around 1024, 1024^2, 1024^3, large tera values, undefined, and `NaN`. Browser smoke tests should verify templates append the expected unit text.
