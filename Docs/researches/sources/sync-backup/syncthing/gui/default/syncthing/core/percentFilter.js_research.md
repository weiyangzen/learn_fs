# sources/sync-backup/syncthing/gui/default/syncthing/core/percentFilter.js

## Purpose
This filter formats numeric percentage values for compact display in the Syncthing GUI.

## Important APIs, types, and functions
It registers `percent` on `syncthing.core`. The filter returns `'0%'` for undefined values or values below `0.01`, uses `toLocaleString(undefined, { maximumFractionDigits: 2 })` for values below `0.1`, and otherwise uses `toLocaleString(undefined, { maximumSignificantDigits: 2 })`, always appending `%`.

## Control flow
The control flow is a three-branch threshold formatter: suppress tiny values to zero, preserve up to two decimal places for very small non-zero percentages, and use two significant digits for the rest.

## State and persistence behavior
The filter is stateless. Output depends on browser locale formatting.

## Dependencies and integration points
It depends only on JavaScript `Number.toLocaleString` and Angular filter registration. Templates use it for completion, progress, and possibly error/rate percentages.

## Risks
`null`, strings, or `NaN` are not explicitly guarded and may produce surprising output or throw depending on the type. Locale output varies by browser. Inputs are assumed to already be in percent units, not fractions; passing `0.5` renders `0.5%`, not `50%`.

## Test signals
Cover undefined, zero, below `0.01`, between `0.01` and `0.1`, normal values, values over 100, `NaN`, and string inputs if template data may not be numeric.
