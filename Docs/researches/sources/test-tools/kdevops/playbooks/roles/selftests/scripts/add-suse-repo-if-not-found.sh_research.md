<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/scripts/add-suse-repo-if-not-found.sh -->
# sources/test-tools/kdevops/playbooks/roles/selftests/scripts/add-suse-repo-if-not-found.sh

Purpose: helper shell script for Suse selftests dependencies that adds a repository only when it is not already configured.

Important APIs/types/functions: shell commands and conditionals including `zypper`, `grep`, `exit`, `if`.

Control flow: Checks existing zypper repositories, adds the requested repository if absent, and exits with shell status.

State and persistence behavior: Mutates zypper repository configuration on Suse systems.

Dependencies and integration points: Called from Suse dependency tasks to enable packages needed by selftests.

Risks: Repository matching by text can miss aliases or equivalent URLs; adding external repos changes package resolution.

Test signals: Signals are idempotent rerun, repository present after first run, and zypper refresh/install success.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/scripts/add-suse-repo-if-not-found.sh -->
