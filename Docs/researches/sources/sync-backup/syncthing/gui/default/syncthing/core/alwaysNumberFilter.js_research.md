# sources/sync-backup/syncthing/gui/default/syncthing/core/alwaysNumberFilter.js

## Purpose
This AngularJS filter normalizes undefined numeric values to `0` for display paths that should always render a number instead of blank or `undefined`.

## Important APIs, types, and functions
It registers `alwaysNumber` on `syncthing.core`. The returned filter function accepts one input and returns `0` only when `input === undefined`; all other values, including `null`, empty strings, negative numbers, and `NaN`, pass through unchanged.

## Control flow
The filter performs a single strict undefined check and immediate return. There is no async behavior and no dependency injection.

## State and persistence behavior
The filter is stateless and does not persist data.

## Dependencies and integration points
It depends on `syncthing.core` being declared before load. Templates can pipe possibly undefined counters or sizes through `alwaysNumber` before additional formatting.

## Risks
Because only `undefined` is coerced, `null` or `NaN` can still leak to the UI. Combining this filter with numeric formatting filters should account for their handling of non-number inputs.

## Test signals
Template/unit tests should assert `undefined -> 0` and that valid zero, positive, negative, `null`, and string inputs are not modified.
