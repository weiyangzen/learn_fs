# sources/security-integrity/fscrypt/cmd/fscrypt/setup.go

## Purpose
Implements global config creation and per-filesystem metadata setup for the setup command.

## APIs, Types, and Control Flow
`createGlobalConfig` requires root, prompts before replacing an existing config, removes it on confirmation, chooses policy version 2 on kernels at least 5.4 and version 1 otherwise, prints hashing customization text, calls `actions.CreateConfigFile`, and reports success. `setupFilesystem` creates a mountpoint context, checks for already setup state, asks whether all users can create metadata unless `--all-users`, maps that to `filesystem.WorldWritable` or `SingleUserWritable`, calls `Mount.Setup`, and prints permissions summary.

## State, Dependencies, and Integration
Writes global config and `.fscrypt` metadata directories. Depends on kernel version detection, action config creation, filesystem setup modes, current target user, and confirmation prompts.

## Risks and Test Signals
Policy v2 detection uses kernel version rather than a live policy-setting probe, so backports or unusual kernels may be misdetected. Setup tests cover replacement, quiet/force behavior, already setup, missing config, and bad config.
