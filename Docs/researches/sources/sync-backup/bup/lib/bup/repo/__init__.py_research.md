<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/repo/__init__.py -->
# sources/sync-backup/bup/lib/bup/repo/__init__.py

## Purpose
This module selects repository locations and constructs local or remote repository objects from command-line options, environment state, URLs, and client configs.

## Important APIs, Types, And Functions
Important APIs are `public_schemes`, `repo_location_url()`, `main_repo_location()`, `repo_for_url()`, `repo_for_location()`, and `parse_repo_url_arg()`.

## Control Flow
`main_repo_location()` prefers reverse-server mode from `BUP_SERVER_REVERSE`, rejects explicit `-r` in that mode, otherwise returns a default file URL or a `client.Config` built from the remote option. `repo_for_url()` dispatches `file` to `LocalRepo` and `ssh`/`bup`/`bup-rev` to `RemoteRepo`. `parse_repo_url_arg()` parses a bytes URL/path, rejects invalid schemes or malformed file authorities, and calls command misuse handlers on error.

## State And Persistence Behavior
The module does not maintain mutable state. It reads environment and may create a local repository when `repo_for_url(..., create=True)` is requested.

## Dependencies And Integration Points
It depends on `client.Config`, config URL parsing, `URL`, `LocalRepo`, `RemoteRepo`, and `path.defaultrepo()`. Command modules use it to resolve source/destination repositories for save, get, ls, and remote operations.

## Risks And Edge Cases
Reverse mode and explicit remote are mutually exclusive. `repo_location_url()` only accepts `URL` and `client.Config`. File URLs with authority are rejected to avoid ambiguity with extra slashes. Public scheme validation prevents accidental internal schemes from user-facing CLI arguments.

## Test Signals
`test/int/test_repo.py`, remote command tests, `test/ext/test-on`, `test/ext/test-ls-remote`, and get/save CLI tests cover remote option parsing, reverse mode, URL validation, and local/remote construction.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/repo/__init__.py -->
