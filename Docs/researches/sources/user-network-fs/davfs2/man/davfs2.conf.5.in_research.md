# sources/user-network-fs/davfs2/man/davfs2.conf.5.in

## Purpose
This template generates the `davfs2.conf(5)` manpage. It documents system/user configuration precedence, mount-specific sections, syntax and quoting rules, and all major davfs2 configuration options.

## Important APIs and options
The file uses roff man macros with Meson/config placeholders such as `@CONFIGFILE@`, `@PROGRAM_NAME@`, `@SYS_CONF_DIR@`, `@PACKAGE@`, and directory defaults. It documents general options, WebDAV/TLS/auth/lock behavior, cache settings, and debug categories. Notable operational options include certificate trust controls, `secrets`, `ask_auth`, `use_locks`, ETag workarounds, redirects, timeouts, retry limits, `max_upload_attempts`, `add_header`, cache sizing, refresh windows, delayed upload, GUI optimization, and memory minimization.

## Control flow described
The manpage specifies parser semantics: root reads only the system config, ordinary users also read the user config with user settings taking precedence, global options precede mount-specific bracketed sections, and section options override globals for that mount.

## State and persistence behavior
It documents persistent config files, secrets paths, cache directories, cert lookup directories, syslog debug output, lock behavior, local cache lifetime, and backup handling for failed uploads.

## Dependencies and integration points
The template is transformed by the build system and installed as section 5 documentation. It must stay aligned with the shipped `etc/davfs2.conf`, mount helper parser, German PO translations, and `mount.davfs(8)` documentation.

## Risks
The manpage has several spelling issues in source text (`brakets`, `otion`, `thes`, `propably`) and may not include every option from `etc/davfs2.conf` (`sync_on_lookup` appears in config but not here). Security-sensitive options such as `trust_server_cert`, `debug secrets`, `add_header`, and `follow_redirect` require accurate warnings because they affect TLS validation, log exposure, and credential reuse.

## Test signals
Build the generated manpage, run manpage linting, verify placeholder substitution, and compare option names/defaults against parser tables and `etc/davfs2.conf`. Translation update tests should regenerate PO references from this source.
