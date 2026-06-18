# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icharout.h

Declares outline character output helpers.

Key points:
- Declares execution of a character procedure-defined outline.
- Defines `metrics_present` enum for no metrics, width-only, and sidebearing-plus-width cases.
- Declares helpers to retrieve `Metrics`, `Metrics2`, and `CDevProc` entries from base fonts.
- Declares `zchar_set_cache`, which consults metrics/CDevProc and calls `setcachedevice`/`setcachedevice2`, possibly scheduling a continuation.
- Declares CharString data extraction for glyphs.
- Declares glyph enumeration over a dictionary through `dict_first`/`dict_next`.

Research notes:
- This is the shared boundary between font dictionaries, character cache setup, and outline execution.
