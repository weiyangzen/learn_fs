# sources/sync-backup/syncthing/gui/default/syncthing/core/basenameFilter.js

## Purpose
This filter extracts the final path component from a slash- or backslash-separated path for display in the Syncthing GUI.

## Important APIs, types, and functions
It registers the `basename` filter on `syncthing.core`. The filter returns an empty string for `undefined`, splits input on both `/` and `\`, and returns the last segment.

## Control flow
The implementation checks for undefined, splits via the regular expression `/[\/\\]/`, guards against an empty `parts` result, and returns the last array entry.

## State and persistence behavior
The filter is pure and stateless.

## Dependencies and integration points
It depends only on Angular module registration. It is useful in templates that display file names from platform-specific paths.

## Risks
Trailing separators return an empty string because the final split segment is empty. Non-string inputs without a `split` method will throw. It does not account for URL paths, Windows drive semantics, or root-only paths beyond simple separator splitting.

## Test signals
Cover Unix paths, Windows paths, paths with trailing separators, undefined input, simple file names, and accidental non-string input if templates may pass model objects.
