# sources/test-tools/lcov/scripts/context.pm

Purpose: example lcov/geninfo/genhtml `--context-script` callback that returns environment metadata for infrastructure debugging and optionally appends that metadata to lcov comments.

Important APIs: package `context` exports `new`. `new($script, @args)` accepts `--comment`. `context()` returns a hash containing `user`, `perl_version`, `perl`, and optionally `PERL5LIB`.

Control flow and state: construction validates arguments and creates a small blessed array. If `--comment` is present, it immediately calls `context` and pushes `key: value` strings into global `@lcovutil::comments`. The `context` method shells out to `whoami` and `which perl`, then chomps values.

Dependencies and integration: depends on `lcovutil` for comment storage and on the callback protocol that calls `$callback->context()` near tool completion. It is not used by the test Makefiles directly but is a sample support script shipped with lcov.

Risks and test signals: shelling out makes output platform-dependent and can fail in minimal containers. The constructor only accepts bare `--comment`; future option extensions need to preserve callback invocation semantics. Test signals are callback loading tests and any lcov/genhtml run configured with `--context-script context.pm,--comment`.
