# sources/sync-backup/bup/lib/bup/cmd/on.py

## Purpose
`on.py` runs selected bup commands on a remote host over SSH while providing a local protocol server for commands that need repository access. It enables reverse backup/restore-style workflows with constrained server permissions.

## APIs and Control Flow
`run_server` wraps an SSH child with `Conn` and `protocol.Server`. `restricted_repo_config` only allows `init-dir`/`set-dir` requests that match the local repo. `save_or_split_server_config` parses the local command options and vets ref updates so save/split can only update the expected branch with a new commit descending from the previous one. `main(argv)` parses host/port and subcommand, chooses a server config for supported commands, starts remote `on--server`, sends NUL-separated argv with a length prefix, runs local server if needed, and demuxes remote stderr output.

## State, Dependencies, Integration, Risks, Tests
It may update the local repository through a restricted protocol server; the remote host runs the actual bup command. Dependencies include SSH transport, `protocol.Server`, `LocalRepo`, command parsers from save/split, `parse_commit`, and mux/demux. Risks include command authorization gaps, ref-vetting assumptions, unsupported command handling, host parsing with colons, and deadlocks around SSH pipes. Test signals include supported-command matrix, init rejection, restricted repo path enforcement, save/split ref update vetting, remote argv framing, demux output, and return-code propagation.
