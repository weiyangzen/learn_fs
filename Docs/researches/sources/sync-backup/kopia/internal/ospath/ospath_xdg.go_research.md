# sources/sync-backup/kopia/internal/ospath/ospath_xdg.go

Purpose: XDG-based path initialization for Unix-like non-Darwin/OpenBSD/non-Windows systems.

Important APIs/types/functions: `init`.

Control flow: reads relevant XDG environment variables when present and falls back to home-relative defaults for config and logs.

State and persistence behavior: assigns package-global path variables during initialization.

Dependencies and integration points: affects default config and log paths on Linux and related platforms.

Risks and test signals: XDG environment combinations should be tested with isolated process-level tests because init-time state is hard to reset in-process.
