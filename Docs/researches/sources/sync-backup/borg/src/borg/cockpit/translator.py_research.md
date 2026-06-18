# sources/sync-backup/borg/src/borg/cockpit/translator.py

Purpose: provides a small mutable translation layer that can replace selected English UI/log strings with Borg-themed wording.

Important APIs: `BORG_DICTIONARY` maps exact or substring English text to replacement text. `UniversalTranslator(enabled=True)` stores a boolean flag, `toggle()` flips it, and `translate(message)` returns the original message when disabled, exact dictionary match when present, otherwise first substring replacement. Module globals `TRANSLATOR = UniversalTranslator(enabled=False)` and `T = TRANSLATOR.translate` are imported by widgets.

Control flow and state: translation state is global and mutable through `TRANSLATOR.enabled`. The app toggles it and asks widgets to refresh displayed labels.

Dependencies and integration: used by `widgets.py` for labels/log titles and by `app.py` for toggle behavior. No external dependencies.

Risks: substring replacement order follows dictionary insertion order and can change output when keys overlap. `T` is a bound method to the global instance; replacing `TRANSLATOR` would not update existing `T` imports. Translation is not localization-grade and only handles known strings.

Test signals: cover disabled passthrough, exact replacement, substring replacement, toggle behavior, global `T`, and label refresh behavior in widgets after toggle.
