# sources/test-tools/kdevops/playbooks/roles/fstests_prep_localhost/defaults/main.yml

## Purpose
Defines default variables for the `fstests_prep_localhost` role, which installs localhost-side tooling needed to orchestrate fstests and post-process results. These defaults are the role's configuration contract and determine which tasks are active, where artifacts are stored, and which provider/workflow options are used.

## Important APIs, Types, and Functions
The important interface is the file content itself plus the variables it references from role defaults and playbook inventory. The role-level integration surface is the `fstests_prep_localhost` variable namespace plus Ansible facts such as distribution family, hostname, groups, and enabled workflow flags.

## Control Flow
There is no runtime control flow in the file; Ansible loads these values before task execution. Downstream tasks branch on these defaults with `when` clauses, use them as template variables, and sometimes replace them with extra vars or generated facts.

## State and Persistence Behavior
State is declarative role configuration. Values persist only as Ansible variables unless later tasks write files, create mounts, start services, or fetch artifacts based on them.

## Dependencies and Integration Points
Integrated on localhost before driving fstests. It installs Ansible-side packages and Python result tooling such as junitparser.

## Risks
The main risk is missing localhost packages causing late result parsing or orchestration failures rather than target setup failures. File-local risk signals: variable or template changes have broad downstream effects because many tasks consume them indirectly.

## Test Signals
Useful test signals include run the role in Ansible check mode where modules support it; exercise the enabled and disabled `when` branches; verify idempotence on a second playbook run.
