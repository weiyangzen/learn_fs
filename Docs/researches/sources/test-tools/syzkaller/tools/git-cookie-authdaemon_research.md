<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/git-cookie-authdaemon -->
# sources/test-tools/syzkaller/tools/git-cookie-authdaemon

## Purpose

GCE metadata OAuth token daemon that writes Git HTTP cookies for Google source hosts.

## Important APIs, Types, and Functions

Functions `read_meta`, `select_scope`, `configure_git`, `acquire_token`, `update_cookie`, `refresh_loop`; supports `--debug`/`--nofork` and Python 2/3 urllib imports.

## Control Flow

Selects service-account scope, configures global git `http.cookiefile`, writes Mozilla cookies for source hosts with access token expiry, daemonizes unless disabled, refreshes before expiry.

## State and Persistence Behavior

Persists `~/.git-credential-cache/cookie` and global Git config; cleanup removes cookie files on process exit.

## Dependencies and Integration Points

Requires GCE metadata server and supported OAuth scopes; Windows path handling included.

## Risks and Edge Cases

Token cookie on disk requires permissions; first token fetch does not retry; missing scopes exit hard.

## Test Signals

Run on GCE with `--nofork --debug`; mock metadata for scope/token/refresh failures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/git-cookie-authdaemon -->
