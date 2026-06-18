# sources/storage-engines/wiredtiger/test/csuite/config/main.c

Purpose: exhaustive csuite test for WiredTiger precompiled configuration strings for APIs that support `WT_CONNECTION::compile_configuration`. It validates rejection of malformed configs, parameter binding, use of compiled configs, valid/invalid key values, and the verbose reconstruction output for `WT_SESSION.begin_transaction` and `WT_SESSION.reconfigure`.

Important APIs, types, and functions: `PARSE_STATE` records verbose callback state, `CUSTOM_EVENT_HANDLER` embeds `WT_EVENT_HANDLER`, and `KEY_VALUES` describes configuration keys with valid/invalid values and nested subcategories. The key lists cover begin-transaction settings and session reconfigure settings. `COPY_MESSAGE_CONTENT` extracts quoted content from verbose messages. `check_configuration_result` and `check_single_result_against_inputs` parse reconstructed compiled output with `wiredtiger_config_parser_open`. `handle_wiredtiger_message` consumes verbose `configuration:2` messages. `check_compiling_configurations` drives all compile/bind/use/error checks.

Control flow: `main` installs a custom event handler, parses standard test options, recreates the home, opens WiredTiger with `verbose=(configuration:2)`, and opens a session. It then calls `check_compiling_configurations` for `WT_SESSION.begin_transaction` expecting 46 successful reconstruction callbacks and for `WT_SESSION.reconfigure` expecting 89. Each check first confirms generic bad config failures and unsupported method failure, then compiles `isolation=%s`, verifies unbound use fails, binds `snapshot`, uses the compiled configuration on the matching API, compiles an empty string, rejects compiling an already compiled string, tests every invalid value, and then tests every valid value while the message callback validates the reconstructed config.

State and persistence behavior: creates a temporary WiredTiger home with statistics/statistics_log enabled, but does not create application tables. Most state is in the custom event handler and parser allocations, which are freed between compilations.

Dependencies and integration points: depends on the public configuration compiler, config parser, event handler callbacks, session transaction/reconfigure APIs, `test_util` option parsing, and verbose message text containing `for method:`, `input config:`, and `reconstructed config:`.

Risks: the test is intentionally coupled to exact verbose output structure and exact successful-output counts; legitimate changes to verbose messages or supported keys require updating expected counts and key lists. `reconfigure_kv` contains a duplicated `debug` entry, which contributes to the expected output count. Nested subcategory validation supports only one nested level.

Test signals: successful run prints the checked output counts for both methods and exits cleanly. Any parser, compiler, verbose callback, or API use regression should trip `testutil_assert`.
