# sources/test-tools/kdevops/terraform/aws/scripts/gen_kconfig_ami

## Purpose
This executable Python script discovers Linux AMI publishers and AMI name patterns and renders AWS AMI-related Kconfig or raw/Terraform reference output.

## Important APIs, Types, And Functions
`get_known_ami_owners()` defines trusted owner IDs and regex search patterns for AlmaLinux, Amazon, CentOS, Debian, Fedora, Oracle, PyTorch, Red Hat, Rocky, SUSE, and Ubuntu. `discover_ami_patterns()` queries `describe_images`, filters by owner/pattern/state/type, groups AMIs, and emits latest/sample data plus Terraform filter examples. `classify_ami_name()` maps AMI names into OS/version groups. `generate_terraform_pattern()` and helpers derive wildcard filters from sample names. `generate_terraform_example()` emits complete `aws_ami` data-source snippets. Output functions render owners, per-owner distro menus, raw tables, or Terraform examples. `parse_arguments()` supports owner selection, `--owners`, `--format`, `--quiet`, and `--region`.

## Control Flow
`main()` can list known owners without credentials. For discovery it validates AWS credentials, picks an explicit or default region, and either processes one owner or all owners. Full Kconfig mode prints an owners menu, then uses a 10-worker thread pool to discover each owner and renders `distro.j2` sections in deterministic owner order.

## State And Persistence
No local files are written by the script itself; stdout is redirected by Make targets into generated Kconfig files. It reads AWS credentials/config through boto3 and current AMI state from EC2. AMI owner metadata is static in code.

## Dependencies And Integration Points
It depends on `aws_common.py`, `botocore`, `jinja2` templates `owners.j2` and `distro.j2`, and live EC2 AMI APIs. It integrates with `terraform/aws/Kconfig` through generated `Kconfig.ami` content and with Terraform users through example output.

## Risks And Test Signals
The `recent_amis` fallback is computed but grouping still iterates over `matching_amis`, so the time-window filtering currently does not constrain generated patterns. Regex classifications are heuristic and can become stale as publishers rename images. Owner IDs can change, especially marketplace-style publishers. Parallel AWS calls can hit rate limits. Tests should mock `describe_images` pages, exercise classification for every owner, verify pattern generation, confirm no-credentials exit status 0, and render Jinja templates with stable fixture data.
