# sources/test-tools/kdevops/playbooks/roles/terraform/tasks/destroy/main.yml

Purpose: top-level Terraform teardown dispatcher.

Important APIs/types/functions: removes ephemeral SSH config file with `file`, then includes DataCrunch or generic destroy tasks based on provider.

Control flow: deletes `kdevops_ssh_config`, dispatches DataCrunch-specific destroy for DataCrunch, otherwise generic destroy.

State/persistence behavior: removes controller SSH config and destroys cloud resources via included tasks.

Dependencies/integration: depends on `kdevops_ssh_config` and `kdevops_terraform_provider`.

Risks/test signals: removes SSH config before destroy, which can complicate manual access if destroy fails. Test signals are missing generated SSH config and empty Terraform state.
