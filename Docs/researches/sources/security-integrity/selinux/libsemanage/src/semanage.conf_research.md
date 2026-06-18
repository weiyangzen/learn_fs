# sources/security-integrity/selinux/libsemanage/src/semanage.conf

Purpose: sample/default libsemanage configuration file controlling policy store connection and policy generation settings.

Important settings: `module-store = direct` is active. Comments document source/direct/socket/TCP store modes. `policy-version` and `target-platform` are shown as optional commented settings.

Control flow/integration: `semanage_conf_parse` reads this style of file during handle creation. The resulting `semanage_conf_t` controls direct backend selection, policy version, target platform, and many additional settings declared in `semanage_conf.h`.

State/persistence: configuration is read at runtime and influences where/how libsemanage connects and commits. This file does not write state.

Risks: comments mention connection types not implemented by `handle.c` in this source subset; misconfiguration can make `semanage_connect` fail. Test signals include parsing default config, direct connection setup, and overrides for policy version/target platform in config parser tests.
