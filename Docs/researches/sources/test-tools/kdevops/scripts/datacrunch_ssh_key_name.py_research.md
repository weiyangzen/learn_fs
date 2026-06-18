<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_ssh_key_name.py -->
# sources/test-tools/kdevops/scripts/datacrunch_ssh_key_name.py

Purpose: emits a deterministic DataCrunch SSH key name for the current kdevops checkout. The name format is `kdevops-datacrunch-<8-char-md5>`.

Important APIs and functions: `get_unique_key_name()` resolves the git repository root with `git rev-parse --show-toplevel`, falls back to `os.getcwd()`, hashes that path with MD5, and returns the formatted name. `main()` prints it.

Control flow: one lookup/hash/print path; failures to run git are expected and handled by cwd fallback.

State and persistence: no writes. The output depends on absolute checkout path, so moving a repository changes the generated key name.

Dependencies and integration: uses standard library plus external git. It is referenced by `terraform/datacrunch/kconfigs/Kconfig.identity` to provide a default unique SSH key name for DataCrunch provisioning.

Risks: MD5 is used only for stable naming, not cryptographic security, but path disclosure through predictable names may still be a consideration. Different symlink/canonical path contexts can produce different names. Test signals include running inside and outside a git repo and checking stability from subdirectories.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_ssh_key_name.py -->
