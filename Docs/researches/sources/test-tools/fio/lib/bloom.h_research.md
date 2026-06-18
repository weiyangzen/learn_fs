# sources/test-tools/fio/lib/bloom.h

Purpose: exposes the Bloom filter API with an opaque `struct bloom`.

Important APIs/types: `bloom_new`, `bloom_free`, `bloom_set` for `uint32_t` word arrays, and `bloom_string` for byte strings with optional set behavior.

Control flow/state: callers allocate with an expected bit count, insert/check data, and free the map. Return values indicate whether all hash bits were already set, not whether the element is certainly present.

Dependencies/integration: includes fio bool support and integer types. It intentionally hides hash implementation choices.

Risks/test signals: callers must treat positive results as probabilistic and avoid zero-sized filters. Tests should verify set-versus-check mode and stable behavior across hash backends.
