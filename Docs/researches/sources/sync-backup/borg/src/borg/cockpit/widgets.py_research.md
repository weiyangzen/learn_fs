# sources/sync-backup/borg/src/borg/cockpit/widgets.py

Purpose: defines Textual widgets for Borg Cockpit: status counters, live log display, logo/starfield visual panel, pulsar/slogan/logo art, and speed sparkline.

Important APIs: `StatusPanel` uses reactive counters for elapsed time, file status counts, and return code; watcher methods update child labels and classes. `StandardLog.add_line(line)` escapes Rich markup, parses Borg list-status prefixes, updates `StatusPanel` counters, and colorizes output. `Starfield`, `Pulsar`, `Slogan`, and `Logo` render decorative UI. `LogoPanel` composes and positions those elements on resize while avoiding overlap. `SpeedSparkline` keeps fixed history and renders a four-line character chart.

Control flow and state: `StatusPanel` holds `speed_history`; watchers react to state changes. `StandardLog` mutates the app-level status panel based on stream lines. `Starfield` and `LogoPanel` use per-instance random seeds for stable-but-random placement. `Pulsar` and `Slogan` use intervals to toggle CSS classes. `SpeedSparkline.refresh_chart()` normalizes visible history to 0..32 levels.

Dependencies and integration: depends on Textual widgets/containers/reactive fields, Rich `escape`, Borg `classify_ec`, the cockpit theme variables, and global translator state. It expects parent app queries for `#status` and `#standard-log-content`.

Risks: parsing status from log lines is heuristic and marked TODO; output format changes can miscount files. `random.seed(...)` changes global RNG state during rendering/resize, which could affect other UI code. Non-ASCII art/block characters are intentional but may render poorly in some terminals. `max_lines=None` may grow memory for long-running commands.

Test signals: cover each reactive watcher, return-code class mapping, elapsed formatting and translated stardate mode, log parsing for all status prefixes, Rich markup escaping, title/slogan translation refresh, resize positioning without overlap on typical sizes, and sparkline output for empty/constant/high variance data.
