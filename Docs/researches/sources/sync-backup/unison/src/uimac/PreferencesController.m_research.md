<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/PreferencesController.m -->
# sources/sync-backup/unison/src/uimac/PreferencesController.m

Source read: complete file, 89 lines, 2876 bytes, sha256 `5fa728f4cdd2afc2`.

Purpose: Implements the profile creation preferences panel and emits profile initialization requests to the OCaml core.

Important APIs/types/functions: `reset`, `validatePrefs`, `anyEnter:`, `localClick:`, and `remoteClick:`. The OCaml integration point is `ocamlCall("xSSS", "unisonProfileInit", profileName, firstRoot, secondRoot)`.

Implementation inventory: discovered Objective-C/C callback methods include `reset, validatePrefs, anyEnter, localClick, remoteClick`.

Control flow: `reset` clears controls and defaults to remote mode. `validatePrefs` checks profile and root fields, builds either `ssh://user@host/path` or a local second root, shows modal alerts for missing data, and calls OCaml on success. Toggle handlers enable or disable remote user/host fields.

State and persistence behavior: Form widgets are the sole mutable state. No preferences are persisted here; OCaml writes profile files through `unisonProfileInit`.

Dependencies and integration points: Depends on Cocoa, modal alert panels, and the bridge. It is owned and presented by `MyController`.

Risks: Uses bitwise `|` instead of logical `||` in nil/empty checks; this works for BOOL-ish values but does not short-circuit. SSH URL construction does not escape user/host/path characters. `anyEnter:` is noted as broken because it fires for tab/mouse focus changes.

Test signals: Test empty field rejection, local path profile creation, remote profile creation with special characters, and reloading the new profile list after save.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/PreferencesController.m -->
