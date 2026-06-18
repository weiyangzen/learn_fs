# sources/sync-backup/syncthing/lib/syncthing/time_android.go

Purpose: Android-specific timezone initialization workaround.

Important APIs and control flow: `init` runs `/system/bin/getprop persist.sys.timezone`, trims output, loads that location, and assigns `time.Local`. Any command or location error returns without changing local time.

State and persistence: mutates process-global `time.Local`; no file persistence.

Dependencies and integration: built only for Android. It addresses Go timezone behavior on Android.

Risks: shelling out during init can fail silently. It trusts system property content and affects all time formatting/parsing using `time.Local`, including versioner timestamp parsing. No tests in this subset.
