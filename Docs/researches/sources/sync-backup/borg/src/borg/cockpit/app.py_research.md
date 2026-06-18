# sources/sync-backup/borg/src/borg/cockpit/app.py

Purpose: defines the main Textual application for Borg Cockpit, a TUI that runs a Borg command and displays live output/status.

Important APIs: `BorgCockpitApp(App)` sets `TITLE`, `CSS_PATH`, and key bindings; `compose()` builds Header, LogoPanel, StatusPanel, StandardLog, and Footer; `get_theme_variable_defaults()` supplies theme variables; `on_load()` registers/selects the Borg theme; `on_mount()` animates logo/slogan and schedules `start_runner`; `start_runner()` initializes counters/timers and starts `BorgRunner`; `compute_speed()` updates line-rate and elapsed time; `on_unmount()` and `action_quit()` stop resources; `action_toggle_translator()` toggles translations and refreshes labels; `handle_log_event()` routes runner events into widgets.

Control flow and state: app state includes `total_lines_processed`, `last_lines_processed`, `speed_timer`, `start_time`, `process_running`, `runner`, and `runner_task`. The runner command comes from `self.borg_args` or defaults to `["--version"]`. Process completion sets status `rc`; quitting waits for runner shutdown and fades UI elements before exiting.

Dependencies and integration: depends on Textual `App`, widgets, containers, theme, local widgets, `BorgRunner`, and global translator state. It executes Borg indirectly through `runner.py`.

Risks: `action_quit` awaits `runner_task`; if stream processing hangs, exit can hang. `handle_log_event` assumes widgets are mounted and queryable. Speed is based on log lines rather than files, so the unit label is approximate. The app passes arbitrary `borg_args` into the runner, so caller-side argument construction matters.

Test signals: Textual app tests should cover composition IDs, theme registration, runner startup default/custom args, stream-line event handling, process-finished status updates, translator toggle refresh, timer updates, and graceful stop on unmount/quit.
