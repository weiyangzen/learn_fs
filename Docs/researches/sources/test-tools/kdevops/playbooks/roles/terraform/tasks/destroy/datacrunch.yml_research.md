# sources/test-tools/kdevops/playbooks/roles/terraform/tasks/destroy/datacrunch.yml

Purpose: DataCrunch-specific Terraform destroy that works around dev-overrides provider initialization.

Important APIs/types/functions: shell block hides DataCrunch resource `.tf` files, creates minimal provider config, runs `terraform init`, restores files/lockfile, runs `terraform destroy -auto-approve -no-color`, and removes `.terraform.lock.hcl`.

Control flow: initializes external provider with the workaround, destroys resources, then deletes the lock file.

State/persistence behavior: destroys cloud resources, mutates Terraform working files temporarily, rewrites lock file, and removes the final lock file.

Dependencies/integration: depends on DataCrunch Terraform provider behavior and `topdir_path` provider directory.

Risks/test signals: temporary file hiding/restoration is fragile if interrupted; auto-approve is intentionally destructive. Test signals are successful destroy exit, empty Terraform state, and restored `.tf` files.
