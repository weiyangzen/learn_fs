<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_ssh_keys.py -->
# sources/test-tools/kdevops/scripts/datacrunch_ssh_keys.py

Purpose: manages DataCrunch SSH keys through the DataCrunch API, including listing keys, uploading a public key, deleting a remote key, generating a local key pair, and setting up the expected kdevops Terraform key.

Important APIs and functions: `list_ssh_keys()`, `add_ssh_key()`, and `delete_ssh_key()` wrap API endpoints; `generate_unique_key_name()` creates a cwd-based MD5 name; `generate_ssh_key_pair()` invokes `ssh-keygen -t ed25519`; `get_default_key_file()` hashes the git root with SHA256 and returns `~/.ssh/kdevops_terraform_<hash>`; `setup_ssh_key()` generates and uploads if needed; `cleanup_ssh_key()` removes remote keys; `main()` exposes `list`, `add`, `delete`, `setup`, and `cleanup`.

Control flow: the CLI first verifies credentials, then dispatches. Setup checks for an existing remote key by name, creates the local key if absent, reads `.pub`, and posts it. Delete resolves name or ID to an API ID, then attempts a direct HTTP DELETE.

State and persistence: writes local private/public keys under `~/.ssh` when setup generates them; remote state changes in the DataCrunch account; no local deletion during cleanup.

Dependencies and integration: imports `datacrunch_api`, uses external `ssh-keygen` and git. It supports DataCrunch Terraform identity workflows.

Risks: key-name hashing differs from `datacrunch_ssh_key_name.py` because one uses cwd MD5 while the other uses git-root MD5, which can cause mismatched default names. DELETE endpoint behavior is noted as uncertain. Test signals include mocked API calls, temp HOME key generation, idempotent setup with existing remote key, and delete-by-name resolution.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_ssh_keys.py -->
