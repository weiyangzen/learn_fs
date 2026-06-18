# sources/security-integrity/fscrypt/cli-tests/run.sh

## Purpose
End-to-end runner for CLI tests. It creates throwaway ext4 filesystems, a test user, isolated config, normalized output, and compares each test against checked-in expected output.

## APIs and Control Flow
The script parses `--update-output`, requires root and prerequisite commands, creates `TMPDIR`, installs cleanup traps, creates the test user, sets locale/umask/PATH, and runs selected `t_*.sh` tests. `setup_for_test` formats loopback ext4 images with encryption, mounts them, sets `FSCRYPT_ROOT_MNT`, `FSCRYPT_CONSISTENT_OUTPUT`, and `FSCRYPT_CONF`, runs global setup with v2-policy check, and sets up the data mount. `run_test` executes a test, filters unstable values, compares output, and optionally updates expected output.

## State, Dependencies, and Integration
Depends on root, `mkfs.ext4`, `losetup`, `mount`, `expect`, `keyctl`, `useradd`, and `chpasswd`. It drives the built `../bin/fscrypt` binary copied into temp space.

## Risks and Test Signals
The runner is intentionally destructive within temp loop devices and test user accounts. Output filtering masks temp paths, devices, config path, descriptors, and protojson spacing, creating stable golden tests for real filesystem behavior.
