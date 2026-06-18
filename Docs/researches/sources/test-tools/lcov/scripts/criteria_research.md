# sources/test-tools/lcov/scripts/criteria

Purpose: thin executable wrapper for the `criteria.pm` genhtml criteria callback. It decodes the JSON coverage summary argument and exits according to the callback result.

Important APIs: the script imports `criteria::new`, `lcovutil`, and `JsonSupport::decode`. Its command-line contract is `name type json-string [--signoff]` although the module supports additional coverage-type flags.

Control flow and state: it constructs `criteria->new($0, @ARGV)`, then parses `--signoff` again with `GetOptions`, pops the JSON string, decodes it, calls `$obj->check_criteria(@ARGV, $db)`, prints all returned messages, and exits with the status.

Dependencies and integration: lib paths are set relative to the script and support-scripts install location. This wrapper is used when callback invocation prefers an external process rather than loading `criteria.pm` directly.

Risks and test signals: parsing options both in `criteria->new` and again in the wrapper can consume or validate arguments unexpectedly, especially for module-only options. The script assumes `JsonSupport` is provided by `lcovutil`. Tests should exercise external `--criteria-script path/criteria` usage, failing JSON summaries, and `--signoff` suppress behavior.
