# sources/sync-backup/git-lfs/lfshttp/standalone/standalone.go

Purpose: Implements the standalone `file://` transfer agent protocol for copying LFS objects between local repositories without an API server.

Important APIs/types/functions: `inputMessage`, `errorMessage`, `outputErrorMessage`, `completeMessage`, `fileHandler`, `fileUrlFromRemote`, `gitDirAtPath`, `fixUrlPath`, `newHandler`, `dispatch`, `respond`, `upload`, `download`, and `ProcessStandaloneData`.

Control flow: `ProcessStandaloneData` reads newline-delimited JSON messages, creates a handler from the first message's remote, dispatches init/upload/download/terminate, and writes JSON responses. Upload links/copies local object into remote object storage unless already present. Download verifies remote object existence, creates a temp output path, and links/copies from remote object storage.

State and persistence behavior: Reads config/remotes and remote Git object storage. Writes uploaded objects to remote filesystem, creates temporary download files under configured temp dir, and removes handler temp dir at end. `gitDirAtPath` temporarily changes process cwd while invoking `git rev-parse`.

Dependencies and integration points: Integrates `config.Configuration`, `lfsapi.EndpointFinder`, `lfs.LinkOrCopy`, remote LFS filesystem, `subprocess.ExecCommand`, Git executable, and transfer-agent JSON protocol.

Risks and edge cases: Process-wide `os.Chdir` is risky if called concurrently. Only `file://` remotes are accepted. Windows URL path handling is special-cased. Handler creation failures are reported as JSON error messages before returning.

Test signals: No direct tests in this subset; behavior depends on integration coverage elsewhere.
