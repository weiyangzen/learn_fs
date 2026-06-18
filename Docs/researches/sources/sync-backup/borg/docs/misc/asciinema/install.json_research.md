# sources/sync-backup/borg/docs/misc/asciinema/install.json

Purpose: asciinema v2 terminal recording showing standalone Borg binary installation. The first line is the cast header with terminal dimensions, timestamp, and environment; the remaining lines are JSON event arrays with output timing and payloads.

Important APIs and control flow: consumers are asciinema-compatible players or documentation embed logic, not Borg runtime code. The event stream types out a narrative, downloads `borg-linux64` and `borg-linux64.asc` from a Borg GitHub release, verifies the detached signature with `gpg --verify`, installs to `/usr/local/bin/borg`, adjusts ownership and executable bits, and checks `borg -V`.

State and persistence: persisted state is only documentation media. The demonstrated workflow writes a binary into `/usr/local/bin`, uses local GPG keyring trust state, and depends on downloaded release artifacts.

Dependencies and integration points: integrates with Borg docs pages that embed terminal casts, GitHub release URLs, GPG signature verification, sudo, and asciinema v2 parsing.

Risks: the recording is pinned to Borg 1.2.1 while nearby docs are Borg 2-style, so version drift is likely. The JSON is newline-delimited cast data, not one JSON object. Release URLs, signer keys, and standalone binary names can become stale.

Test signals: validate with an asciinema player or line-oriented JSON parser; confirm the header parses, every event line is valid JSON, and docs render the cast without treating the file as strict single-document JSON.
