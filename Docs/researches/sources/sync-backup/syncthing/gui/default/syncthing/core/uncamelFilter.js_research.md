# sources/sync-backup/syncthing/gui/default/syncthing/core/uncamelFilter.js

## Purpose
The `uncamel` AngularJS filter converts camelCase or mixed identifier-like configuration keys into user-facing labels while preserving reserved acronyms and expanding common time suffixes.

## Important APIs, Control Flow, And State
The filter registers `uncamel` and returns a function that accepts a string. It first returns an empty string for non-string or empty input. It replaces reserved substrings such as `IDs`, `ID`, `URL`, `API`, `QUIC`, `TCP`, `LAN`, and binary units with placeholders, inserts spaces between lowercase/digit and uppercase transitions, restores placeholders with spacing, expands final suffixes `S`, `M`, `H`, and `Ms` into time units, title-cases non-reserved parts, collapses whitespace, and trims. State is function-local: `reservedStrings`, placeholder map, and counter.

## Dependencies And Integration Points
It depends only on AngularJS filter registration and modern JavaScript features such as `const`, `let`, arrow functions, and `Object.entries`. It integrates with advanced config or metadata views that need readable labels from schema keys.

## Risks And Test Signals
Ordering in `reservedStrings` matters, as longer strings must be protected before their substrings. The use of unescaped words in `RegExp(word, 'g')` is safe for the current word list but should be reconsidered if new reserved strings contain regex metacharacters. The suffix expansion is heuristic and only applies to the final space-separated part. Unit tests should cover `deviceIDs`, `apiKey`, `rescanIntervalS`, `pullerPauseS`, `QUICLAN`, and binary unit labels.
