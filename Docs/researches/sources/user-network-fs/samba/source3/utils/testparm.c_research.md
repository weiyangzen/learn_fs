# sources/user-network-fs/samba/source3/utils/testparm.c

## Purpose

`sources/user-network-fs/samba/source3/utils/testparm.c` implements `testparm`, the Samba configuration syntax and logic checker. It loads `smb.conf`, reports global and per-share configuration problems, can dump full or filtered configuration, can list all parameters, and can test host allow/deny access decisions. The source was read as a complete 1231-line file.

## Important APIs, Types, and Functions

Key functions are `main`, `do_global_checks`, `do_per_share_checks`, `do_idmap_check`, `lp_scan_idmap_found_domain`, `idmap_config_int`, `pw2kt_check_line`, `pw2kt_validate_spn_spec`, and `directory_exist_stat`. Local structs `idmap_config` and `idmap_domains` hold discovered idmap backend/range data.

## Control Flow

`main` initializes cmdline/loadparm, parses options such as `--suppress-prompt`, `--verbose`, `--skip-logic-checks`, `--show-all-parameters`, `--parameter-name`, and `--section-name`, loads the selected config with registry shares, reports weak crypto state, runs global/per-share checks unless skipped, and dumps configuration or host access decisions. `do_global_checks` performs hard-coded warnings/errors for security modes, WINS settings, directories, socket options, password sync, idmap, crypto hardening, keytab sync, and mixed quoting warnings. `do_per_share_checks` validates hosts allow/deny lists, oplock settings, DOS attribute masks, print command quirks, and mixed `vfs_fruit` usage.

## State and Persistence Behavior

The tool reads configuration and filesystem metadata but does not persist changes. It uses talloc for temporary idmap and parsing data, and writes diagnostics to stderr and config dumps to stdout.

## Dependencies and Integration Points

It integrates with Samba loadparm, registry shares, host access checks, GnuTLS helper state, regex scanning of parametric options, filesystem stat wrappers, Kerberos/keytab configuration, PAM/systemd-userdb build options, and Samba's parameter dump APIs.

## Risks and Edge Cases

The logic checks encode security policy assumptions and version-specific warnings, so stale checks can create noisy or missing diagnostics. Idmap scanning caps the temporary discovered-domain array at 32 entries. Some loops scan service numbers from 0 to 999, depending on `VALID_SNUM`. Mixed quoting warnings reference CVE-driven substitution behavior and must stay aligned with actual substitution semantics.

## Test Signals

Tests should cover valid and invalid smb.conf loading, filtered parameter/section dumps, host allow/deny checks, idmap range overlap and autorid range-size checks, ADS/domain security requirements, directory permission warnings, password sync validation, crypto hardening warnings, `sync machine password to keytab` parser cases, and per-share VFS/printing/oplock validations.
