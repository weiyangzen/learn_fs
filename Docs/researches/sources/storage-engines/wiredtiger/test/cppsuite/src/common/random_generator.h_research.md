# sources/storage-engines/wiredtiger/test/cppsuite/src/common/random_generator.h

Purpose: Declares the cppsuite random-generator singleton and character-set options.

Important APIs/types/functions: `characters_type` selects pseudo-alphanumeric or alphabet-only data. `random_generator::instance`, string generators, `generate_bool`, and templated `generate_integer` are the public API.

Control flow: singleton copy/assignment are deleted; integer generation uses a uniform distribution over caller-supplied bounds.

State and persistence: owns a Mersenne Twister, distributions, and character constants per thread in the implementation.

Dependencies/integration: included by data-generation and workload helpers.

Risks and test signals: callers must pass valid min/max bounds and choose appropriate string mode for keys versus compressible values. There is no explicit test hook for seeding.
