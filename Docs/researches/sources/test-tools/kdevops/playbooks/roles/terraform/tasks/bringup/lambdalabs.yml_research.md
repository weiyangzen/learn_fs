# sources/test-tools/kdevops/playbooks/roles/terraform/tasks/bringup/lambdalabs.yml

Purpose: Lambda Labs-specific Terraform bringup with API key checks, wildcard tier selection, capacity probing, tfvars updates, and Terraform apply.

Important APIs/types/functions: `set_fact`, shell `scripts/lambdalabs_credentials.py check`, `lambdalabs_select_tier.py`, `lambdalabs_check_capacity.py`, inline Python for capacity response parsing, `fail`, `lineinfile`, and `cloud.terraform.terraform`.

Control flow: defines wildcard tiers, validates API key configuration, selects instance/region for wildcard tiers, validates output shape, writes selected instance and region to `terraform.tfvars`, computes resolved instance type, runs a capacity check for explicit selections, reports capacity failures, then invokes Terraform state-present apply.

State/persistence behavior: mutates `terraform/lambdalabs/terraform.tfvars`, reads local credential storage, and creates Terraform state/cloud instances.

Dependencies/integration: depends on Lambda Labs credentials helper, capacity/selection scripts, Terraform provider configuration, and generated variables such as `terraform_lambdalabs_instance_type` and `terraform_lambdalabs_region`.

Risks/test signals: API capacity is volatile; scripts must return exactly expected stdout formats. Test signals are credential check success, two-token tier selection output, tfvars update, and successful Terraform apply.
