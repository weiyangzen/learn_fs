# sources/sync-backup/syncthing/gui/default/syncthing/development/logbar.js

## Purpose
This development-only script intercepts console warnings and errors and increments counters in a developer top bar. It helps GUI developers see when console noise appears during manual testing.

## Important APIs, Control Flow, And State
`intercept(method, handler)` wraps `window.console[method]`, calls the handler with the method name, then forwards the original console call using `apply` when available or a joined string fallback for old IE. `handleConsoleCall(type)` looks for `#log_<type>`, marks it with `hasCount`, displays `#dev-top-bar`, and increments the element's numeric `innerHTML`. At load time, if `window.console` exists, it intercepts `error` and `warn`.

## Dependencies And Integration Points
It uses browser DOM APIs and `window.console`. It expects DOM elements with IDs such as `log_error`, `log_warn`, and `dev-top-bar` in the development GUI layout.

## Risks And Test Signals
Repeated loading would wrap console methods multiple times and overcount. The counter assumes existing numeric `innerHTML`. Since it monkey-patches global console behavior, it should remain excluded from production bundles. Manual development smoke tests can confirm counts increment and original console output still appears.
