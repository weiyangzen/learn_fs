# sources/sync-backup/borg/src/borg/cockpit/theme.py

Purpose: defines the Textual theme object used by Borg Cockpit.

Important APIs: module-level `theme = Theme(...)` names the theme `"borg"` and sets primary, secondary, error, warning, success, accent, foreground, background, surface, panel, dark mode, and custom variables for cursor, selection, starfield, pulsar, and logo colors.

Control flow and state: static module-level object creation only. No persistence.

Dependencies and integration: consumed by `BorgCockpitApp.on_load`, widgets that read `theme.variables`, and Textual's theme system.

Risks: color variables are referenced by string keys in widgets; renaming/removing variables can break rendering. The high-contrast green-on-black palette is deliberate but may need accessibility review for broader use.

Test signals: import smoke test, app theme registration, and widget rendering tests for required variable keys.
