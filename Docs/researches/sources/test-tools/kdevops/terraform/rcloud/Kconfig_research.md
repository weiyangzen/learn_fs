# sources/test-tools/kdevops/terraform/rcloud/Kconfig

Purpose: rcloud Terraform provider Kconfig fragment, gated by `TERRAFORM_RCLOUD`. It exposes the minimal configuration needed to talk to an rcloud REST API and select a base image.

The two symbols are `TERRAFORM_RCLOUD_API_URL`, defaulting to `http://localhost:8765`, and `TERRAFORM_RCLOUD_BASE_IMAGE`, defaulting to `debian-13-generic-amd64-daily`. Help text explains local versus remote API URLs and the expected base image directory on the rcloud server.

Control flow is just Kconfig conditional inclusion. State persists as selected string values that downstream Terraform or Ansible code consumes. Integration points are the rcloud REST server, guestfs-created base images, and kdevops defconfig-rcloud setup.

Risks include no validation of URL syntax, no authentication/TLS settings, and a hardcoded default base image that may not exist on a given server. Test signals should parse the Kconfig fragment, verify yaml/export behavior where expected by downstream code, and run a configuration fixture with non-default API URL and image name.
