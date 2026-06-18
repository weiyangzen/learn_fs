<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/doc_update.py -->
# sources/storage-engines/wiredtiger/test/evergreen/doc_update.py

Purpose: pushes already-generated documentation updates to a GitHub Pages repository using a GitHub App installation token.

Control flow and APIs: defines context manager `cwd(path)` to temporarily change directories. At module execution it reads `GITHUB_APP_ID` and `GITHUB_APP_PRIVATE_KEY`, creates `AppAuth` and `GithubIntegration`, reads `GITHUB_OWNER` and `GITHUB_REPO`, finds the app installation for that repo, obtains an installation access token, changes into `wiredtiger.github.com`, and runs `git push https://'<app_id>:<token>'@github.com/<owner>/<repo>`.

State and persistence: reads environment secrets and pushes the current local commit in `wiredtiger.github.com`; it does not generate docs itself.

Dependencies and integration: invoked by Evergreen documentation update workflow after docs are built and committed. Depends on PyGithub, git, environment variables, and local repository layout.

Risks and test signals: uses `subprocess.run([cmd], shell=True)`, mixing list and shell mode. Token appears in the command string, though not printed by the script. All exceptions exit with their message. Missing env vars are explicitly validated.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/doc_update.py -->
