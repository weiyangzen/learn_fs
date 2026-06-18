# sources/sync-backup/borg/docs/usage/serve.rst.inc

Purpose: Documents `borg serve`, the repository server process used by SSH-launched remote repositories and long-running socket server mode.

Important APIs/types/functions: CLI contract is `borg [common options] serve [options]`. Options include repeatable `--restrict-to-path PATH`, repeatable `--restrict-to-repository PATH`, and `--permissions` overriding `BORG_REPO_PERMISSIONS`. The described permission modes are `all`, `no-delete`, `write-only`, and `read-only`.

Control flow: Runtime starts a server process, accepts repository requests from clients, enforces path/repository restrictions, enforces permission policy, and runs until the SSH/socket connection terminates or the service is stopped.

State and persistence: The server itself is a process/session state holder. Repository persistence depends on granted permissions: read-only prevents writes; no-delete permits new data but prevents deleting/overwriting existing data; write-only prevents reading existing data.

Dependencies and integration points: Integrates with remote repository URLs, SSH command startup, socket repositories, `BORG_REPO_PERMISSIONS`, and repository backend access control. The source tree also has tests around `rest_serve_command` invoking `borg serve --rest`.

Risks: Misconfigured restrictions can expose more repositories than intended. The command ignores `--repo`/`BORG_REPO`; clients specify the repository, so server-side restriction policy is the trust boundary.

Test signals: Cover restriction resolution, empty/nonexistent final repository path initialization, permission modes, SSH command construction, socket mode, and attempts to read/write/delete outside granted policy.
