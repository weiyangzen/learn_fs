# Research: sources/user-network-fs/samba/source4/setup/wscript_build

Purpose: Waf build/install declarations for Samba setup templates and schema data.

Important APIs: `bld.INSTALL_WILDCARD()` installs groups of schema, display-specifier, adprep, and templated setup files under `${SETUPDIR}`. `bld.INSTALL_FILES()` installs explicit update lists such as `dns_update_list` and `spn_update_list`.

State and integration: it does not execute provisioning; it determines which static setup assets are installed into the build prefix for provisioning and upgrade tools to consume.

Risks and test signals: missing wildcard coverage can produce runtime provisioning failures despite successful compilation. Build/install tests and provisioning blackbox tests are the main signals.
