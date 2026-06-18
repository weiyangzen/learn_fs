<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/main-localhost.yml -->
# sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/main-localhost.yml

Purpose: installs localhost dependencies for 9p selftests builds required to build and run Linux kernel selftests.

Important APIs/types/functions: modules `ansible.builtin.import_tasks`; tasks `Debian-specific setup for localhost`.

Control flow: Uses OS-specific package tasks and, for Suse, repository setup where needed. The localhost variant runs once on the controller when 9p builds are enabled.

State and persistence behavior: Mutates package/repository state on targets or localhost.

Dependencies and integration points: Included by `selftests/tasks/install-deps/main.yml` or directly for localhost 9p builds.

Risks: Dependency drift is common across kernel selftests; missing libraries often appear as make failures rather than install failures.

Test signals: Signals are successful package install, selftests build success, and availability of special tools such as configfs/radix-tree dependencies.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/main-localhost.yml -->
