# sources/test-tools/kdevops/playbooks/roles/fio-tests/defaults/main.yml

## Purpose
Defines default variables for the `fio-tests` role, which formats or mounts test storage, generates fio job files, runs fio workloads, and collects result archives. These defaults are the role's configuration contract and determine which tasks are active, where artifacts are stored, and which provider/workflow options are used.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `fio-tests` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no runtime control flow in the file; Ansible loads these values before task execution. Downstream tasks branch on these defaults with `when` clauses, use them as template variables, and sometimes replace them with extra vars or generated facts.

## State and Persistence Behavior
State is declarative role configuration. Values persist only as Ansible variables unless later tasks write files, create mounts, start services, or fetch artifacts based on them.

## Dependencies and Integration Points
Integrated as a benchmark workflow role. It depends on fio, optional plotting packages, filesystem tools, generated job templates, remote archive/fetch operations, and localhost result directories.

## Risks
High-risk areas are destructive mkfs/unmount operations, long-running async fio jobs, CPU/cache tuning assumptions, and result archive/fetch path mismatches. File-local risk signals: variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run; run a small smoke workload; verify remote artifacts are fetched to the expected localhost result directory.
