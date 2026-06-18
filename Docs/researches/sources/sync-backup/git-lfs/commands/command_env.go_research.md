<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_env.go -->
# sources/sync-backup/git-lfs/commands/command_env.go

Purpose: implements `git lfs env`, printing version, Git version, endpoint/auth configuration, environment-derived LFS settings, and configured filter commands for diagnostics.

Important APIs/types/functions: `envCommand`, `config.ShowConfigWarnings`, `git.Version`, `config.VersionDesc`, `cfg.Remotes`, `cfg.IsDefaultRemote`, `getAPIClient().Endpoints`, `lfs.Environ`, and `getTransferManifest`.

Control flow: enables config warnings, prints Git LFS and Git version data, prints default remote endpoint with auth and SSH metadata, prints non-default remote endpoints, dumps the computed LFS environment, then prints `filter.lfs.process`, `filter.lfs.smudge`, and `filter.lfs.clean` config values.

State and persistence behavior: read-only except for lazy API client and transfer manifest creation. Output goes through the shared `Print` writer and may be captured in error buffers used for logs.

Dependencies/integration points: integrates configuration, endpoint discovery, auth access mode reporting, SSH metadata parsing, transfer adapter manifest construction, and filter install state.

Risks and test signals: risks include exposing sensitive endpoint/auth mode context, forcing lazy client creation in a diagnostic command, and config warnings changing output stability. Test signals include repositories with default and multiple remotes, SSH remotes, missing Git version, and installed/uninstalled filter config.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_env.go -->
