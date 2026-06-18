# sources/test-tools/kdevops/scripts/lambdalabs_ssh_key_name.py

## Purpose
`lambdalabs_ssh_key_name.py` generates a deterministic, unique Lambda Labs SSH key name based on the current working directory. This helps separate kdevops deployments by workspace.

## Important APIs, Types, And Functions
Functions are `get_directory_hash(path, length=8)`, `get_project_name(path)`, `generate_ssh_key_name(prefix="kdevops", include_project=True)`, and `main()`.

## Control Flow
The generator hashes the absolute current directory with SHA256, derives a project label from the last two non-generic path components, sanitizes underscores/dots and non-alphanumeric characters to hyphens, joins prefix/project/hash, collapses duplicate hyphens, and shortens to `prefix-hash` if longer than 50 characters. CLI `--simple` omits the project component.

## State And Persistence
No files are written. Output depends deterministically on `os.getcwd()`.

## Dependencies And Integration Points
Depends on Python standard `hashlib`, `os`, and `sys`. It integrates with Lambda Labs SSH key provisioning/validation scripts and Terraform/Kconfig identity settings.

## Risks And Edge Cases
Directory-derived names can change if a workspace is moved. Generic path filtering is simple and may produce surprising labels. Hash length of 8 hex chars is usually enough for local uniqueness but not collision-proof. Provider-side naming constraints beyond length/alphanumeric/hyphen are not checked.

## Test Signals
Test stable hashes for fixed paths, project extraction from root/generic/non-generic paths, sanitization, long-name truncation, `--simple`, `--help`, and unknown-option exit.
