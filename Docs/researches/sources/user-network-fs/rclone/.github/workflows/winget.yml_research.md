# sources/user-network-fs/rclone/.github/workflows/winget.yml

Purpose: Publishes rclone releases to the Windows Package Manager repository.

Important APIs/types/functions: Triggered on release `released`. Uses `vedantmgoyal2009/winget-releaser@v2` with identifier `Rclone.Rclone`, installer regex `-windows-\w+\.zip$`, and `WINGET_TOKEN`.

Control flow: On release, the action finds matching Windows zip installers and submits/updates the WinGet manifest.

State and persistence: Side effects occur in the WinGet packaging ecosystem, not in this repository.

Dependencies and integration points: Depends on release assets, GitHub token secret, and the winget-releaser action.

Risks: Regex must match current asset naming. Token permissions and external WinGet validation can fail after release.

Test signals: Action success and downstream WinGet PR/manifest publication are the validation signals.
