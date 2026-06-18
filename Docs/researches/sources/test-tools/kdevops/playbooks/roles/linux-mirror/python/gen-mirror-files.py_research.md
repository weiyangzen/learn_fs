# Research: sources/test-tools/kdevops/playbooks/roles/linux-mirror/python/gen-mirror-files.py

`sources/test-tools/kdevops/playbooks/roles/linux-mirror/python/gen-mirror-files.py` is a Python support tool in the kdevops `linux-mirror` role. Role context: builds local Linux source mirrors served through git daemon, systemd timers, and optional NFS. The file is 176 lines / 5329 bytes and was read in full for this report.

## Purpose

This Python helper supports `linux-mirror` by performing controller-side automation that is awkward to express directly in Ansible. It defines functions `main` and classes none found.

## Important APIs, Types, And Functions

Imports: `argparse`, `json`, `os`, `pathlib`, `pprint`, `subprocess`, `sys`, `time`, `yaml`. Important call sites include `ArgumentParser`, `Exception`, `add_argument`, `close`, `exists`, `exit`, `format`, `get`, `isfile`, `main`, `open`, `parse_args`, `remove`, `replace`, `safe_load`, `write`. CLI argument declarations include `"--yaml-mirror", metavar="<yaml_mirror>", type=str, default=default_mirrors_yaml, help="The yaml mirror input file.",`, `"--verbose", const=True, default=False, action="store_const", help="Be verbose on otput.",`, `"--refresh", metavar="<refresh>", type=str, default="360m", help="How often to update the git tree.",`, `"--refresh-on-boot", metavar="<refresh>", type=str, default="10m", help="How long to wait on boot to update the git tree.",`.

## Control Flow

The script runs from top-level CLI parsing into helper functions, then performs filesystem/process operations for the role. The `if __name__ == "__main__"` entry point, when present, makes it usable from Ansible `shell`/`command` tasks. Loops and conditionals derive work from configuration files, command-line options, and local repository paths.

## State And Persistence

Persistent targets and path-like references include none found. The script can create or rewrite generated files and may invoke subprocesses; its state is therefore visible in the linux-mirror role directory and local systemd/mirror artifacts rather than in Python memory after exit.

## Dependencies And Integration Points

It depends on Python standard/library modules `argparse`, `json`, `os`, `pathlib`, `pprint`, `subprocess`, `sys`, `time`, `yaml`, local kdevops layout, and Ansible tasks that call it with the repository root as the working directory. Generated outputs are consumed by subsequent Ansible copy/systemd tasks.

## Risks And Edge Cases

Risks include malformed mirror YAML, missing repository-relative paths, subprocess failures, partial writes of generated unit files, and root/user systemd scope mismatches. Because the script is invoked from automation, clear nonzero exits and stderr are important for diagnosing mirror setup failures.

## Test Signals

Run the script with representative CLI arguments in a temporary checkout, verify generated files, and run Python syntax/import checks. In the role, follow with Ansible tasks that load the generated YAML and inspect systemd service/timer status.
