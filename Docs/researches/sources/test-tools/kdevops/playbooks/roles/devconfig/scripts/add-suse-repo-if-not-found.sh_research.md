<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/scripts/add-suse-repo-if-not-found.sh -->
# sources/test-tools/kdevops/playbooks/roles/devconfig/scripts/add-suse-repo-if-not-found.sh

Source read: complete file, 18 lines, 371 bytes, sha256 `b84c26e677669093`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/devconfig/scripts/add-suse-repo-if-not-found.sh_research.md`.

Purpose: helper shell script to ensure a SUSE zypper repository exists and is enabled, while removing existing YaST-related repositories first.

Important APIs/types/functions: positional args `REPO_URL` and `REPO_NAME`; `zypper lr -d`, `grep yast2`, `awk`, `zypper rr`, `zypper mr -e`, `zypper ar -f -c`, and `zypper --non-interactive --gpg-auto-import-keys refresh`.

Control flow: collect repo ids whose detailed listing contains `yast2`; remove each; try enabling the requested repo; exit success if enable works; otherwise add the repo with refresh/check enabled and refresh it.

State and persistence behavior: mutates zypper repository configuration and refresh metadata.

Dependencies and integration: likely called from devconfig SUSE repo setup tasks to add kernel/tooling repos only if missing.

Risks: unquoted variables and shell word splitting can break URLs/names with spaces. Removing every repo matching `yast2` is broad. Output redirection order `2>&1 > /dev/null` leaves stderr not fully suppressed as likely intended.

Test signals: run on disposable SUSE images with existing repo, missing repo, and YaST repos present; verify only intended repos are removed and the target repo is enabled/refreshed.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/devconfig/scripts/add-suse-repo-if-not-found.sh -->
