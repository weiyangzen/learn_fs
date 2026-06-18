# sources/user-network-fs/rclone/bin/manage_backends.py

Purpose: manages backend metadata YAML files under docs/data/backends. Verbs create default files, update canonical/default fields, or fetch live feature/hash/precision data via `rclone backend features`.

Important pieces: canonical key ordering and defaults, `test_server` context manager for optional local test server startup, `wait_for_tcp`, YAML load/save, `fetch_rclone_features`, `do_create`, `do_update`, and `do_features`. State changes are YAML writes and temporary environment variables for test server configuration. Dependencies include PyYAML, rclone, optional init scripts, sockets, subprocesses, and test servers. Risks include modifying docs metadata in place, environment leakage if server setup fails outside context, simplistic remote-name derivation, Unicode YAML output, and requiring reachable test servers. Test signal is command output and updated YAML diffs.
