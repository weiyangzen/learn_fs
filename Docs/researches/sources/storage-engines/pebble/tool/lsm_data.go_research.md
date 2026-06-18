## sources/storage-engines/pebble/tool/lsm_data.go

Purpose: generated asset container for the LSM HTML viewer. It embeds CSS and JavaScript strings used by `lsm.go` when `--embed` is enabled.

Important APIs/types/functions: `lsmDataCSS` defines layout, slider, labels, and SVG classes. `lsmDataJS` builds DOM elements with D3, defines level heights/offsets, humanized sizes, slider behavior, keyboard playback, and the central `version` object. The `version` object manages current level/sublevel file arrays, edit index, add/remove operations, L0 sublevel rebuilding, level info, rendering, mouse-over overlap highlighting, resizing, and slider/index input synchronization.

Control flow: on `window.onload`, JavaScript initializes sublevel counts from `data.Edits`, sets SVG sizing, and applies edit zero. `version.set` steps forward or backward by applying/unapplying add/delete deltas, rebuilds L0 sublevels from recent `Sublevels` maps, sorts L0 by sequence numbers and other levels by key range, updates labels, and renders. `updateSize` rebuilds slider ticks/drag handle and clip paths. Keyboard handlers support left/right stepping and spacebar playback.

State and persistence: browser-only state is held in JavaScript arrays and SVG DOM. No persistent storage is used. Input comes from the global `data` object emitted by `lsm.go`.

Dependencies and integration: depends on D3 v5, either loaded remotely when embedded or from `tool/data/d3.v5.min.js` when not embedded. Generated from `tool/data/lsm.css` and `tool/data/lsm.js` by `make_lsm_data.sh`.

Risks: generated file should not be manually edited. Embedded mode still references remote D3, so fully offline viewing requires `--embed=false` plus local assets. Rendering relies on numeric object keys from JSON and D3 v5 event globals. Some comments and misspellings indicate legacy frontend code; layout is fixed-height SVG oriented.

Test signals: no direct frontend test in this subset. `lsm.go` compilation and `lsm_test.go` indirectly validate that the generated strings exist and are consumed.
