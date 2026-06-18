## sources/sync-backup/syncthing/lib/osutil/lowprio_windows.go

Purpose: Windows implementation for lowering process priority.

Important API: `SetLowPriority` opens the current process and sets priority class to idle/background-equivalent through Windows syscalls.

Control flow and state: the function calls Windows process priority APIs and returns wrapped errors on failure.

Dependencies and integration points: selected on Windows builds for startup priority configuration.

Risks: Windows permissions/API availability can cause failures; behavior differs from Unix nice values.

Test signals: no direct tests in this subset.
