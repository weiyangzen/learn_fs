# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/exec.c

Abaco command dispatch, selection commands, search/look behavior, new window creation, and plumber integration.

Key responsibilities:
- Defines the tag command table (`Back`, `Cut`, `Del`, `Get`, `Google`, `New`, `Paste`, `Stop`, etc.).
- Expands clicked text into executable command names or search/look terms.
- Implements editing commands using `Text` and page selection state.
- Implements navigation/history commands and page loading from URL tags.
- Sends look targets to plumber or searches selected text.
- Opens pages in existing matching windows or newly made windows.
- Handles incoming plumb messages for web targets.

Important behavior:
- Middle-click executes commands; right-click looks/plumbs/searches.
- `Cut`/`Snarf` operate on page selection if `selpage` is set, otherwise on text selection.
- `Get` reloads or loads from the URL tag and records history only when URL changes.
- `Google` builds a query URL with percent-encoded argument text.

Dependencies:
- Uses `Text`, `Page`, `Window`, `Column`, `Row`, snarf/plumb helpers, URL validation, and page loading.

Notable risks:
- Command lookup is prefix/word based after whitespace trimming; tag contents must avoid ambiguity.
- `look3()` falls back from plumber to local search, so plumber availability changes user-visible behavior.
