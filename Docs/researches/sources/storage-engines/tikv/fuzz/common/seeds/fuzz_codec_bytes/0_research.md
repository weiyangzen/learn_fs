# sources/storage-engines/tikv/fuzz/common/seeds/fuzz_codec_bytes/0

## Purpose
Provides an initial seed corpus input for the `fuzz_codec_bytes` target.

## Important APIs, Types, and Functions
The file is raw corpus data rather than code. Its bytes are ASCII `Hello, World!`.

## Control Flow
Fuzzer drivers pass the containing seed directory to AFL/libFuzzer/Honggfuzz. The bytes are fed as input data to `fuzz_codec_bytes`.

## State and Persistence Behavior
Static repository seed. Fuzzers may derive expanded corpora in separate corpus output directories, but this seed file itself is unchanged during normal runs.

## Dependencies and Integration Points
Used by `fuzz/cli.rs::get_seed_dir` when the target name is `fuzz_codec_bytes`; otherwise the CLI falls back to default seeds.

## Risks
The seed is tiny and exercises only simple byte encoding paths at startup. It is useful for bootstrapping but not broad coverage by itself.

## Test Signals
Verify the file is non-empty and that `cargo run -p fuzz -- run <fuzzer> fuzz_codec_bytes` picks this seed directory. Corpus minimization and coverage reports should confirm additional interesting cases are learned.
