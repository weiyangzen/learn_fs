# sources/sync-backup/borg/docs/usage/general/environment.rst.inc

Purpose: central reference for Borg environment variables, automation hooks, directory locations, build variables, and jsonargparse-derived env names.

Important APIs and control flow: documents repository defaults, passphrase sources and precedence (`BORG_PASSPHRASE`, command, FD, new/display/debug passphrases), modern exit-code mode, host ID, lock wait, logging config, remote shell/path, repository permissions, cache suffix/TTL, chunks archive usage, system info, msgpack checks, FUSE implementation order, self-tests, workarounds, output formats, automatic prompt answerers, platform-specific directory discovery through `platformdirs`, key file override, temp directories, and build prefixes.

State and persistence: environment controls repository selection, credentials, cache/config/data/runtime/security/key directories, temporary files, and runtime behavior. Some values can expose secrets or bypass safety prompts.

Dependencies and integration points: config precedence, logging.conf example, platformdirs, XDG/macOS/Windows paths, jsonargparse `default_env=True`, remote transports, locking, FUSE, cache, and setup/build scripts.

Risks: passphrases in environment can leak to other processes; automatic yes-sayers can bypass critical safety prompts; workarounds are emergency-only; disabling msgpack checks or selftests can mask corruption/compatibility problems.

Test signals: env precedence tests, secret-source priority, platform directory resolution, auto-answer validation, generated `BORG_<SUBCOMMAND>__<OPTION>` mappings, and build env handling.
