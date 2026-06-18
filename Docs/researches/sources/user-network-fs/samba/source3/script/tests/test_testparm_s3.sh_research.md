# sources/user-network-fs/samba/source3/script/tests/test_testparm_s3.sh

## Purpose
This test validates Samba 3 `testparm` parsing and logic for special handlers, macro expansions, deprecated-option warnings, share `copy`, and `sync machine password to keytab` grammar.

## Important APIs, Functions, and Control Flow
It accepts `LOCAL_PATH`, writes temporary configs to `$LOCAL_PATH/smb.conf.tmp`, defines `TESTPARM` with `--suppress-prompt --skip-logic-checks`, and `TESTPARM_LOGIC` without skip-logic. Helpers write one-off configs: `test_include_expand_macro`, `test_one_global_option`, `test_one_global_option_logic`, `test_copy`, `test_testparm_deprecated`, and `test_testparm_deprecated_suppress`. The main flow tests valid and invalid `name resolve order`, core global options, include expansions for macro letters `U G D I i L N M R T a d h m v w V`, share copy, deprecated warning emission/suppression, and a positive/negative suite of `sync machine password to keytab` forms.

## State, Dependencies, Integration, and Risks
State is a temporary smb.conf removed at the end. It depends on `testparm`, `subunit.sh`, `testit_grep`, and exact warning text. Risks include output wording drift and no trap cleanup if interrupted. Test signals are command success/failure, expected failures for invalid config, and grep validation for deprecation behavior.
