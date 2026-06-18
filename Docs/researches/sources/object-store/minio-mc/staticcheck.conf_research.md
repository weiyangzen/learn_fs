## sources/object-store/minio-mc/staticcheck.conf

Purpose: Staticcheck configuration for the mc repository. It enables all checks and disables `S1016`.

Control flow and runtime state are absent; this is tooling configuration consumed by Staticcheck. The integration point is CI or local lint invocation. Disabling `S1016` means Staticcheck will not suggest converting struct literals between identical types, likely preserving explicit conversions or public API clarity used in the codebase. Risks are limited to lint coverage: disabling a style check can hide simplification opportunities but avoids noisy or undesirable rewrites. Test signal is external through lint jobs, not code tests.
