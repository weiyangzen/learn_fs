# sources/sync-backup/borg/src/borg/archiver/version_cmd.py

Purpose: implements `borg version`, printing client and server versions in Borg's simplified negotiated version format.

Important APIs: `VersionMixIn.do_version(args)` parses `borg.__version__`, then either uses the client version as the server version for current repository access or opens `LegacyRemoteRepository(..., lock=False)` when `args.location.proto == "ssh"` and `--from-borg1` is active. It prints `client / server` through `format_version`. `build_parser_version(...)` defines the subcommand and explanatory epilog.

Control flow and state: this command is read-only and normally performs no repository I/O for current repositories. The only remote query path is legacy SSH Borg 1.x, where a remote repository object exposes `server_version`.

Dependencies and integration: integrates with `borg.version.parse_version`, `format_version`, `legacy.remote.LegacyRemoteRepository`, the shared parser, and the location/v1 flags supplied by top-level argument parsing.

Risks: output intentionally loses precision because it uses the version tuple format, while `borg --version` can show more detail. Legacy remote behavior depends on `--from-borg1`; without it, the command reports the local client version for both sides.

Test signals: verify local/current output, legacy SSH remote server query, no lock acquisition for version, and formatting behavior for prerelease/local version strings.
