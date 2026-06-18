# sources/sync-backup/syncthing/gui/default/syncthing/core/localeNumberFilter.js

## Purpose
This filter formats a number using the browser's current locale-aware `toLocaleString()` behavior.

## Important APIs, types, and functions
It registers `localeNumber` on `syncthing.core`. The returned function calls `input.toLocaleString()` with no explicit locale or options.

## Control flow
There is no branching; input is expected to provide a `toLocaleString` method.

## State and persistence behavior
The filter is stateless. Output depends on browser locale/runtime settings, not app-managed persistence.

## Dependencies and integration points
It depends on JavaScript's built-in `toLocaleString`. Templates use it for user-facing numeric values where grouping and decimal separators should follow browser defaults.

## Risks
`undefined` or `null` inputs throw because the filter does not guard them. Output can vary by browser and user locale, which may make tests brittle. It does not necessarily align with the selected GUI translation language because no explicit locale is passed.

## Test signals
Tests should include normal numbers, large numbers, decimal values, and guarded calling contexts for undefined/null. Prefer assertions on method invocation or broad formatting shape over exact separators unless locale is fixed.
