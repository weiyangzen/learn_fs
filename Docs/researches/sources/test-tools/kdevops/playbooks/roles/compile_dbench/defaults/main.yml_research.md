<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/compile_dbench/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/compile_dbench/defaults/main.yml

Source read: complete file, 6 lines, 183 bytes, sha256 `3fe74b866bbd25e9`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/compile_dbench/defaults/main.yml_research.md`.

Purpose: defaults for optional dbench source compilation.

Important APIs/types/functions: `compile_dbench`, `dbench_data`, and `dbench_git`.

Control flow: no tasks; defaults are consumed by `compile_dbench/tasks/main.yml`.

State and persistence behavior: enabled runs clone into `{{ data_path }}/dbench` and may install dbench system-wide.

Dependencies and integration: supports filesystem benchmark workflows needing the kdevops dbench fork.

Risks: default false avoids source build; no version pin is provided, so enabled builds track repository default branch.

Test signals: with defaults the clone/build/install tasks should skip; with `compile_dbench=true`, the checkout should appear at `dbench_data`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/compile_dbench/defaults/main.yml -->
