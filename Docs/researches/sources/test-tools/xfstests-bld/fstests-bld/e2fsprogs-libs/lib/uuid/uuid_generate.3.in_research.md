# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_generate.3.in

Purpose: manpage template for UUID generation APIs: default, random, and time-based UUID creation.

Important APIs, types, and functions: documents `uuid_generate(uuid_t out)`, `uuid_generate_random(uuid_t out)`, and `uuid_generate_time(uuid_t out)`.

Control flow: documentation only, but it describes the generation selection logic: `uuid_generate()` prefers high-quality randomness from `/dev/urandom`; if unavailable, it falls back to time, local MAC address when available, and pseudo-random data. `uuid_generate_random()` forces all-random format, and `uuid_generate_time()` forces the time/MAC algorithm.

State and persistence: installed documentation. The described implementations may consume system entropy and may depend on machine/network identity and time; those side effects are outside this template.

Dependencies and integration points: should match generation implementation and public constants in `uuid.h.in`. `tst_uuid.c` checks generated random UUIDs are type 4 and generated time UUIDs are type 1, with DCE variant.

Risks: the text has historical wording and typos such as "subsituted" and "elemntary". Privacy warning for time/MAC UUIDs is important and must stay visible. If the implementation changes entropy sources or daemon use, this page needs updates.

Test signals: generation tests should verify version bits, variant bits, parse/unparse round trips, and behavior under entropy-source failure if feasible. Documentation generation should verify placeholders are substituted.
