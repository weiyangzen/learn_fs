# sources/test-tools/kdevops/playbooks/ai.yml

Purpose: main AI workflow setup orchestrator. It imports the installation playbook for vector database setup while intentionally leaving benchmarks to separate `make ai-tests` targets.

Important APIs/types/functions: uses `ansible.builtin.import_playbook: ai_install.yml`, guarded by `ai_workflow_vector_db | default(true) | bool`, and tags the import as `ai` and `setup`.

Control flow: when the vector DB workflow flag is true, control transfers to `ai_install.yml`; no benchmark or result tasks are run from this setup entrypoint.

State/persistence behavior: this file creates no state directly. Its state impact is whatever `ai_install.yml` and its roles create, especially Docker/Milvus storage and services.

Dependencies/integration: integrates Make targets and AI workflow Kconfig with the install role stack. It assumes `ai_install.yml` is present and that benchmark execution is handled by `ai_tests.yml` or related targets.

Risks/test signals: because it is only an import wrapper, failures show up in imported playbooks. Test signals are Ansible parseability, correct conditional skip when `ai_workflow_vector_db=false`, and successful tag selection.
