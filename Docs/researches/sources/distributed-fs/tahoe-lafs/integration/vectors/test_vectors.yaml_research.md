# Research: sources/distributed-fs/tahoe-lafs/integration/vectors/test_vectors.yaml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007886`: lines 1-8052, `Docs/researches/chunks/subset-b-007886_research.md`
- `subset-b-007887`: lines 8053-16081, `Docs/researches/chunks/subset-b-007887_research.md`
- `subset-b-007888`: lines 16082-18002, `Docs/researches/chunks/subset-b-007888_research.md`

## Chunk Research

### subset-b-007886: lines 1-8052

# sources/distributed-fs/tahoe-lafs/integration/vectors/test_vectors.yaml lines 1-8052

## Purpose

This chunk is the opening portion of Tahoe-LAFS's generated capability test-vector fixture. It is YAML data, not executable code, and it records precomputed upload capabilities for a matrix of deterministic inputs. Each vector describes the plaintext sample to synthesize, the convergence secret to configure, the object/capability format to upload, the ZFEC share parameters to use, and the exact URI capability expected from Tahoe-LAFS.

The surrounding integration suite uses this file to lock Tahoe-LAFS capability generation against known-good outputs. `integration/vectors/vectors.py` loads the full file from `DATA_PATH`, validates the persisted `version`, converts rows into hashable `Case` objects, and exposes `capabilities`. `integration/test_vectors.py` parametrizes `test_capability` over that dictionary, reconfigures an `alice` node with each case's convergence and ZFEC parameters, uploads deterministic data, and asserts the resulting capability string equals the `expected` URI.

Lines 1-8052 contain 162 vector entries and stop in the middle of the 162nd entry's PEM-encoded RSA private key. The full YAML document continues after this chunk and only declares `version: 2023-01-16.2` at the end of the file, so this chunk by itself is intentionally not a standalone YAML document.

## Data Contract and Important Types

Each list item under top-level `vector:` follows the schema consumed by `load_capabilities`:

- `convergence`: base64-encoded 16-byte convergence secret. This chunk uses `YWFhYWFhYWFhYWFhYWFhYQ==` for `b"aaaaaaaaaaaaaaaa"` and `ZOyIygCyaOW6GjVnihtTFg==` for the first 16 bytes of `sha256(b"Hello world")`.
- `expected`: exact capability URI produced by Tahoe-LAFS for the case. CHK entries use `URI:CHK:<storage-index>:<verify-cap>:<required>:<total>:<size>`. Mutable entries use `URI:SSK:...` for SDMF and `URI:MDMF:...` for MDMF.
- `format.kind`: either `chk` or `ssk`. CHK rows have `params: null`; SSK rows carry mutable parameters.
- `format.params.format`: `sdmf` or `mdmf` for mutable cases.
- `format.params.key`: a PEM `RSA PRIVATE KEY` captured during vector generation so mutable cap generation is repeatable.
- `format.params.mutable`: `null` in this chunk.
- `sample.length` and `sample.seed`: instructions for building test plaintext via `stretch(seed, length)`, which repeats the decoded seed and truncates to the desired byte length.
- `zfec.required`, `zfec.total`, and `zfec.segmentSize`: share reconstruction threshold, total shares, and segment size used when reconfiguring the test node.

The Python-side types represented by these YAML fields are `Case`, `Sample`, `SeedParam`, and `Param` from `integration/vectors/vectors.py` and `integration/vectors/model.py`. `Case.data` materializes plaintext from `Sample`; `Case.params` realizes `SeedParam` against the format's maximum share count; `load_format` maps `kind: chk` to `CHK.load(...)` and `kind: ssk` to `SSK.load(...)`.

## Chunk Coverage

Within lines 1-8052, the matrix is highly regular:

- 162 vector starts and 162 `expected` values are visible.
- 54 rows are `chk`; 108 rows are `ssk`.
- Mutable rows split evenly between `sdmf` and `mdmf` in the visible complete field counts: 54 each.
- 120 visible completed ZFEC parameter blocks use `required: 1`; 41 use `required: 2`. The final visible MDMF row begins before its trailing sample/ZFEC block appears, so one `required: 2,total: 3,segmentSize: 131072` block is in the next chunk.
- 60 visible completed ZFEC parameter blocks use `total: 1`; 101 use `total: 3`.
- All visible completed ZFEC blocks use `segmentSize: 131072`, matching `parameters.SEGMENT_SIZE`.
- The first convergence secret accounts for 90 vector starts in this chunk; the second accounts for 72.

The tested sample lengths visible here are `56`, `1024`, `4096`, `131071`, `131073`, `2097151`, `2097153`, `4194304`, `8388607`, and `8388609`. These correspond to the generator's object descriptions around small non-LIT data, one-segment boundaries (`128 KiB - 1` and `+ 1`), and larger segment-multiple boundaries.

## Control Flow and Integration

The data lifecycle starts in `skiptest_generate` in `integration/test_vectors.py`. That helper constructs the Cartesian product of:

- `parameters.ZFEC_PARAMS`
- `parameters.CONVERGENCE_SECRETS`
- `parameters.OBJECT_DESCRIPTIONS`
- `parameters.FORMATS`

For each case, the generator reconfigures the Tahoe node, customizes mutable formats so they have concrete RSA keys, uploads deterministic data, and calls `save_capabilities`. `save_capabilities` serializes the same fields visible here: convergence, format description, sample descriptor, ZFEC parameters, and expected cap.

At test time, `vectors.py` calls `safe_load` on the full file, checks `data["version"] == CURRENT_VERSION`, decodes base64 bytes, constructs `SeedParam`, `Sample`, and loaded `CHK`/`SSK` format objects, then returns a dictionary keyed by `Case`. `test_capability` replays each case by calling `alice.reconfigure_zfec(..., (1, required, total), convergence, segment_size)`, uploads `case.data` in `case.fmt`, and compares the resulting cap to the stored `expected`.

This YAML file therefore sits at the integration boundary between the Python test harness, Tahoe node configuration, mutable key handling, CHK/SSK/MDMF URI generation, convergent encryption, and ZFEC encoding.

## State and Persistence Behavior

The file is a persistent golden dataset. It has no runtime state of its own, but it persists state that would otherwise be nondeterministic or expensive to regenerate:

- The expected capability URIs encode Tahoe-LAFS's historical output for specific parameter combinations.
- Mutable `ssk` entries persist per-case RSA private keys. Without these PEM keys, SDMF and MDMF capabilities would change when regenerated.
- The convergence secrets and sample seeds are base64 text so binary values survive YAML serialization.
- The top-level version field, outside this chunk at the end of the full file, gates loader compatibility. If the version differs from `CURRENT_VERSION`, `load_capabilities` returns no cases.

Because `safe_load` is applied to the whole file, the end-of-file `version` field and all continuation lines after 8052 are required for normal operation. A chunked research reader must not treat lines 1-8052 as parseable YAML.

## Dependencies

The visible data depends on the schema and behavior of:

- `yaml.safe_load` and `yaml.safe_dump` for round-tripping simple YAML values.
- Base64 helpers `encode_bytes` and `decode_bytes` for convergence secrets and sample seeds.
- Tahoe integration format helpers `CHK` and `SSK`, including `CHK.load`, `SSK.load`, `SSK.customize`, and each format's URI-generation behavior during upload.
- `stretch(seed, size)`, which deterministically expands each sample seed into test plaintext.
- `parameters.SEGMENT_SIZE`, fixed at `128 * 1024`.
- Tahoe node reconfiguration through `Client.reconfigure_zfec`, including happy/required/total share settings and convergence secret propagation.
- The upload helper in `integration.util`, which uploads the generated plaintext and returns a capability string.

## Risks and Edge Cases

- The YAML file stores real-looking RSA private keys for deterministic test vectors. They are test fixtures, but tooling should still avoid leaking them into logs unnecessarily or treating them as production secrets.
- The full file places `version` after the large `vector` list. Loaders that stream only the beginning, or chunk consumers that parse partial content, cannot validate compatibility.
- Lines 1-8052 end mid-PEM. Any line-based chunk merge must preserve exact ordering and indentation; otherwise the full YAML scalar for the final visible key will be corrupted.
- Capability strings are exact golden values. Intentional changes to URI encoding, convergence hashing, segment splitting, mutable-key handling, or ZFEC parameter realization will cause broad test failures and require regenerating vectors with a deliberate version bump.
- The vectors include sizes just below and above segment boundaries. These are sensitive to off-by-one errors in segment layout, Merkle tree construction, and CHK URI size fields.
- CHK and mutable formats have different maximum-share semantics in the model. Later full-file chunks cover `MAX_SHARES` cases; this first chunk already exercises `total: 1` and `total: 3`.
- Because `load_capabilities` returns a dictionary keyed by `Case`, duplicate logical cases later in the file would silently overwrite earlier expected strings. The regular product structure makes duplicates unlikely, but generator or serialization changes should keep this in mind.

## Test Signals

Strong test signals from this chunk include:

- Loading the full fixture should produce `Case` instances whose sample data lengths match the listed `sample.length` values and whose decoded convergence secrets are exactly 16 bytes.
- For each complete row in this chunk, upload output should equal the stored `expected` URI for the matching format, sample, convergence, segment size, and ZFEC tuple.
- CHK cases should have `format.params: null` and expected URIs ending with the original plaintext length.
- SDMF and MDMF cases should use persisted PEM keys and produce `URI:SSK:` and `URI:MDMF:` prefixes respectively.
- Boundary sizes `131071`, `131073`, `2097151`, `2097153`, `8388607`, and `8388609` should be preserved exactly; replacing them with rounded segment sizes would invalidate the vectors.
- Re-running `skiptest_generate` without intentional fixture refresh should not be part of normal CI, because these tests are meant to compare against the originally captured outputs rather than moving outputs.

## Chunk Boundary Notes

This chunk begins at the start of the file and captures the `vector:` key and many complete vector entries. It ends at line 8052 inside the RSA private key scalar for a `URI:MDMF:qxw7uvec...` vector with convergence `ZOyIygCyaOW6GjVnihtTFg==`, sample length `131071`, and ZFEC settings that start in the immediately preceding complete CHK/SSK rows. The continuation of that PEM key, its `mutable`, `sample`, and `zfec` fields, plus the remaining matrix rows and final `version` field, are outside this work item and must be handled by later chunks before producing the final per-file research document.

### subset-b-007887: lines 8053-16081

# sources/distributed-fs/tahoe-lafs/integration/vectors/test_vectors.yaml lines 8053-16081

## Purpose

This chunk is part of Tahoe-LAFS' persisted integration-test capability vector corpus. The YAML records pre-generated upload inputs and the exact capability string expected after uploading those inputs through a Tahoe node. The consumer is `integration/test_vectors.py::test_capability`, which parametrizes over `integration.vectors.capabilities`, reconfigures Alice's node to the vector's ZFEC/convergence settings, uploads the generated sample bytes in the requested format, and asserts that the produced capability exactly matches the persisted `expected` value.

The selected line window is a large middle slice of the YAML vector list. It begins inside an MDMF RSA private-key scalar from the previous record and ends inside an SDMF RSA private-key scalar from the next record. Between those boundaries, the chunk contains 160 vector records that both start and finish inside the range, plus the closing part of the leading MDMF record and the opening part of the trailing SDMF record.

## Data Model And Fields

Each vector record uses the same schema loaded by `integration/vectors/vectors.py::load_capabilities`:

- `convergence`: base64-encoded 16-byte convergence secret, later decoded into `Case.convergence`.
- `expected`: Tahoe capability string. This chunk includes `URI:CHK`, `URI:SSK`, and `URI:MDMF` write capabilities.
- `format.kind`: either `chk` for immutable CHK uploads or `ssk` for mutable uploads.
- `format.params`: `null` for CHK, or an SSK parameter object with `format` set to `sdmf` or `mdmf`, a PEM RSA private `key`, and `mutable: null`.
- `sample.length` and `sample.seed`: compact plaintext description. The loader expands this with `stretch(seed, length)` rather than storing large test bodies directly.
- `zfec.required`, `zfec.total`, and `zfec.segmentSize`: encoding parameters used to reconfigure the node before upload.

The chunk exercises the fixed segment size `131072` throughout. The sampled object lengths appearing in this slice are `56`, `1024`, `4096`, `131071`, `131073`, `2097151`, `2097153`, `4194304`, `8388607`, and `8388609`, so it covers small non-LIT CHK input, one-segment boundary-adjacent inputs, and multi-segment Merkle-tree cases.

## Parameter Coverage

Within the selected lines there are 161 `- convergence:` starts, 54 `URI:CHK` expectations, 54 `URI:SSK` expectations, and 53 `URI:MDMF` expectations. Because the line window cuts through scalar blocks, these counts are best read as chunk-internal starts rather than whole-file totals.

The chunk covers both convergence secrets used by the generator:

- `YWFhYWFhYWFhYWFhYWFhYQ==`, the base64 form of `b"aaaaaaaaaaaaaaaa"`.
- `ZOyIygCyaOW6GjVnihtTFg==`, the first 16 bytes of `sha256(b"Hello world")`.

The ZFEC combinations in this slice include:

- `required: 2`, `total: 3`.
- `required: 3`, `total: 10`.
- `required: 71`, `total: 255`.
- `required: 101`, with CHK vectors materializing the symbolic max as `total: 256` and SDMF/MDMF vectors using `total: 255`.

That `255` versus `256` distinction is intentional. `integration/util.py::SSK.max_shares` caps SDMF/MDMF at 255 because those formats encode `N` and `k` directly into one byte, while `CHK.max_shares` is 256.

## Important APIs, Types, And Control Flow

The persisted YAML is interpreted by `integration/vectors/vectors.py`:

- `Case` holds `seed_params`, `convergence`, `seed_data`, `fmt`, and `segment_size`.
- `Sample` describes deterministic plaintext as repeated seed bytes plus a final length.
- `SeedParam.realize(max_total)` resolves symbolic maximum share counts per format.
- `load_format` maps `kind: chk` to `CHK.load` and `kind: ssk` to `SSK.load`.
- `load_capabilities` returns a `dict[Case, str]` from the YAML's `vector` list.

The test flow is:

1. `test_capability` receives one `Case` and expected capability from `vectors.capabilities.items()`.
2. `alice.reconfigure_zfec` writes `shares.happy`, `shares.needed`, `shares.total`, convergence secret, and `shares._max_immutable_segment_size_for_testing` as needed, restarting the node when configuration changes.
3. `upload(alice, case.fmt, case.data)` creates a temporary file from `Case.data`.
4. `CHK.to_argv()` contributes no extra CLI flags; `SSK.to_argv()` writes the persisted RSA private key to a temporary file and passes `--format=sdmf|mdmf --mutable --private-key-path=<temp>`.
5. `tahoe put` returns the capability string, which is compared byte-for-byte to `expected`.

The generator path, `skiptest_generate`, produced records from the Cartesian product of ZFEC parameters, convergence secrets, object descriptions, and formats. It uses `SSK.customize()` to generate RSA keys and `save_capabilities()` to persist the resulting YAML.

## State And Persistence Behavior

The YAML is durable golden-test state, not runtime application state. Its embedded RSA private keys are test fixtures required to make mutable SDMF/MDMF writecaps reproducible. CHK vectors are deterministic from plaintext, convergence secret, and encoding settings; SSK/MDMF vectors also depend on the stored private key.

At test runtime, the file is loaded once into `vectors.capabilities`. Each case mutates the Alice node configuration, possibly restarts the node, performs a single upload, and then discards temporary plaintext and temporary private-key files. The persisted vector file itself is only rewritten by the disabled generation helper.

## Dependencies And Integration Points

This chunk integrates with:

- PyYAML `safe_load` / `safe_dump` for vector serialization.
- `attrs` frozen classes for hashable `Case`, `Sample`, `Param`, and `SeedParam` values.
- Tahoe CLI behavior for `tahoe put`, including immutable CHK and mutable SDMF/MDMF upload paths.
- Tahoe client config keys for shares, convergence secret, and immutable segment size.
- Tahoe URI parsing/formatting in `src/allmydata/uri.py`, including `URI:CHK`, `URI:SSK`, and `URI:MDMF`.
- ZFEC encoding/decoding behavior via Tahoe's immutable and mutable upload implementations.
- RSA serialization support in the integration helper for generated mutable keys.

## Risks And Maintenance Notes

- The line range cuts through PEM scalar blocks. Chunk-level analysis should avoid treating the first and last records as independently valid YAML fragments.
- Any behavioral change in URI serialization, convergence hashing, segment sizing, mutable key handling, or ZFEC share-count semantics will intentionally break these golden vectors.
- The file stores many RSA private keys. They are test-only fixtures, but tooling should avoid logging or copying them unnecessarily.
- `CURRENT_VERSION` in `vectors.py` gates loading. If the YAML version changes without the loader version changing, the capability set becomes empty and the slow vector test would silently have no cases unless the test harness also guards for this.
- Large plaintexts are generated by repetition from small seeds. This gives deterministic coverage for segment-boundary behavior, but it is not high-entropy file-content coverage.
- The SSK max-share cap is format-specific. A mistaken normalization of `MAX_SHARES` to `256` for mutable vectors would create invalid or non-representable SDMF/MDMF cases.

## Test Signals

The main signal is `integration/test_vectors.py::test_capability`, marked slow. Passing this test means the current implementation can still regenerate every capability in the persisted corpus for the same inputs. This chunk specifically signals compatibility for mid-to-high ZFEC configurations (`2/3`, `3/10`, `71/255`, and `101/max`), both convergence secrets, all three upload formats, and object sizes around important segment boundaries.

Adjacent coverage in `integration/test_get_put.py::test_upload_download_immutable_different_default_max_segment_size` checks cross-version immutable segment-size download compatibility, while these vectors pin exact capability outputs for the older fixed `128 KiB` segment size used by the vector generator.

### subset-b-007888: lines 16082-18002

# sources/distributed-fs/tahoe-lafs/integration/vectors/test_vectors.yaml lines 16082-18002

## Scope

This chunk covers the tail of Tahoe-LAFS capability test vector data in `integration/vectors/test_vectors.yaml`. The assigned line range begins in the middle of the PEM private key for the SDMF case that starts at line 16064, then continues through the final complete vector records and the top-level `version: 2023-01-16.2` field at line 18002. Because this is YAML data rather than executable code, the important API surface is the persisted schema consumed by `integration/vectors/vectors.py` and exercised by `integration/test_vectors.py`.

## Purpose

The file is a persisted compatibility oracle for Tahoe-LAFS capability generation. Each vector describes:

- a 16-byte convergence secret encoded with base64;
- a target object format, either immutable CHK or mutable SSK with `format: sdmf` or `format: mdmf`;
- deterministic sample plaintext instructions, made from a base64 seed repeated/truncated to `sample.length`;
- ZFEC parameters, including `required`, `total`, and `segmentSize`;
- the expected read/write capability URI produced by `tahoe put`.

This chunk specifically covers high-share-count cases where `required` is `101` and `total` is the maximum supported by each format: `256` for CHK and `255` for SDMF/MDMF. It also covers the second configured convergence secret (`ZOyIygCyaOW6GjVnihtTFg==`, the first 16 bytes of `sha256(b"Hello world")`) across the whole object-size sample set.

## Schema And Important Data Shapes

Visible records use the same repeated YAML item structure:

- `convergence`: base64 text decoded to bytes by `decode_bytes`.
- `expected`: a Tahoe capability URI. CHK records include URI fields for storage index, verify cap hash, required shares, total shares, and size. Mutable records use `URI:SSK:` for SDMF and `URI:MDMF:` for MDMF.
- `format.kind`: `chk` or `ssk`.
- `format.params`: `null` for CHK; for SSK, a mapping with `format` (`sdmf` or `mdmf`), `mutable: null`, and a PEM RSA private `key`.
- `sample.seed` and `sample.length`: input to `stretch(seed, length)`, so large plaintexts are generated without storing large byte arrays in the YAML.
- `zfec.required`, `zfec.segmentSize`, and `zfec.total`: used to reconfigure the Tahoe node before upload.

The chunk contains 37 top-level vector starts in-range, plus the trailing fields of the SDMF record that began just before the chunk. The complete in-range record starts are:

- First convergence secret `YWFhYWFhYWFhYWFhYWFhYQ==` (`b"aaaaaaaaaaaaaaaa"`): MDMF for 4 MiB, then CHK/SDMF/MDMF triples for `8388607` and `8388609` bytes.
- Second convergence secret `ZOyIygCyaOW6GjVnihtTFg==`: CHK/SDMF/MDMF triples for `56`, `1024`, `4096`, `131071`, `131073`, `2097151`, `2097153`, `4194304`, `8388607`, and `8388609` bytes.

The sample lengths intentionally sit around thresholds: smallest non-LIT CHK input (`56`), small single-segment inputs, one byte below and above the 128 KiB segment size, one byte below and above 16 segments, exactly 32 segments, and one byte below and above 64 segments. This range helps detect off-by-one behavior in segment splitting, Merkle tree construction, and capability derivation.

## Consumer APIs And Types

`integration/vectors/vectors.py` is the direct reader/writer:

- `DATA_PATH` points to this YAML file.
- `CURRENT_VERSION` must match the file's `version`; otherwise `load_capabilities` prints a version mismatch and returns no cases.
- `Case` is an attrs-frozen key type containing `seed_params`, `convergence`, `seed_data`, `fmt`, and `segment_size`.
- `Case.data` calls `stretch(seed, length)` to materialize the plaintext.
- `Case.params` realizes symbolic max-share parameters against the selected format's `max_shares`.
- `load_format` maps `format.kind` to `CHK.load` or `SSK.load`.
- `load_capabilities` converts each YAML record into a `dict[Case, str]` mapping case inputs to expected capability URI.
- `save_capabilities` is the inverse used by the disabled generator path and emits this schema with ASCII-safe YAML.

Supporting model objects in `integration/vectors/model.py` include `Sample`, `Param`, and `SeedParam`. `SeedParam.realize(max_total)` is important for these records because the source parameter set uses a symbolic max-share intent, while the persisted YAML has already resolved it to `256` for CHK and `255` for mutable formats.

Format integration lives in `integration/util.py`:

- `CHK.kind == "chk"` and `CHK.max_shares == 256`; it contributes no extra CLI arguments.
- `SSK.kind == "ssk"` and `SSK.max_shares == 255`; `SSK.to_argv` writes the persisted PEM key to a temporary file and invokes `tahoe put --format=<sdmf|mdmf> --mutable --private-key-path=<temp>`.
- `upload` writes materialized case data to a temporary file, invokes the Tahoe CLI, and returns the stripped capability string.
- `reconfigure` rewrites `shares.needed`, `shares.total`, the private convergence secret, and the test-only immutable segment-size config before restarting the node when necessary.

## Control Flow

The runtime verification path is:

1. Importing `integration.vectors` opens `test_vectors.yaml` and calls `load_capabilities`.
2. `yaml.safe_load` parses the whole document into a mapping with `version` and `vector`.
3. Each record is decoded into a `Case`; base64 fields become bytes, CHK/SSK format objects are reconstructed, and SSK private keys remain attached to their case format.
4. `integration/test_vectors.py::test_capability` parametrizes over `vectors.capabilities.items()`.
5. The `alice` Tahoe node is reconfigured to `(happy=1, required=case.params.required, total=case.params.total)`, the vector convergence secret, and the 128 KiB segment size.
6. The deterministic plaintext is uploaded in the requested format.
7. The resulting capability is compared exactly with the YAML `expected` URI.

The generation path is intentionally disabled as `skiptest_generate`. When manually renamed/enabled, it iterates the Cartesian product from `parameters.py`, customizes mutable formats with fresh RSA keys, uploads through Tahoe, and repeatedly rewrites the accumulated YAML via `save_capabilities`.

## State And Persistence Behavior

This chunk is pure persisted test data. It stores deterministic inputs and expected outputs, but no runtime state. The only mutable behavior is external: the generator may overwrite the whole YAML file, and the test path reconfigures a temporary Tahoe client node. SSK/MDMF vectors persist RSA private keys so mutable capability generation is reproducible; losing or changing any key changes the expected mutable capability.

The final `version: 2023-01-16.2` anchors compatibility with `CURRENT_VERSION`. If a future generator changes capability semantics or schema, the version must change in lockstep with loader support or tests will silently skip all loaded vectors by returning `{}` after a mismatch.

## Dependencies And Integration Points

Key dependencies are:

- PyYAML `safe_load`/`safe_dump` for schema parsing and serialization.
- `attrs.frozen` for hashable immutable case objects.
- base64 for ASCII-safe byte fields.
- Twisted `FilePath` for locating the YAML next to the loader.
- Tahoe-LAFS CLI behavior for `tahoe put`, mutable format selection, and returned capability strings.
- Tahoe node configuration for convergence secret, ZFEC share parameters, and `_max_immutable_segment_size_for_testing`.
- RSA key serialization for SDMF/MDMF vectors.

The most important code integration points are `integration/test_vectors.py`, `integration/vectors/vectors.py`, `integration/vectors/parameters.py`, and `integration/util.py`. NEWS notes that these vectors are intended for compatibility verification between Tahoe-LAFS and other implementations, so external implementations may also treat this YAML as an interoperability contract.

## Risks And Edge Cases

- The assigned chunk begins inside a literal PEM block. Chunk-level readers must avoid treating line 16082 as a record boundary; the SDMF vector starts at line 16064.
- SSK and MDMF records contain large PEM private-key scalars. Naive text scans for strings like `URI:` or YAML-looking keys inside scalar bodies can miscount records; top-level indentation or a YAML parser is safer.
- CHK and mutable formats have different maximum share counts. These records depend on `total: 256` for CHK and `total: 255` for SDMF/MDMF; normalizing them would break the vectors.
- Expected capability URIs are exact golden values. Any change in convergence hashing, segment sizing, ZFEC parameter handling, mutable key handling, URI encoding, or Tahoe CLI output formatting can fail the tests.
- The `56` byte case is just above the literal-file cutoff described in `parameters.py`; changing the LIT threshold or immutable upload selection may alter CHK expectations.
- Boundary sizes around `131072`, `2097152`, and `8388608` are deliberate. Off-by-one changes in segment count, padding, or Merkle tree layout are likely to surface here.
- The loader returns an empty capability set on version mismatch after printing a message. That can make `test_capability` collect no parametrized cases instead of producing direct per-vector failures.
- The embedded RSA private keys are test fixtures, not secrets for production use, but accidental replacement or reformatting changes mutable capabilities.

## Test Signals

Primary signal: `integration/test_vectors.py::test_capability` should pass for every loaded case. For this chunk, meaningful coverage includes:

- exact capability equality for CHK, SDMF, and MDMF;
- correct reconstruction of sample data using repeated seeds for lengths from `56` through `8388609`;
- correct reconfiguration of `required=101`, `total=255/256`, convergence secret, and `segmentSize=131072`;
- stable handling of the final `version` field;
- YAML loader tolerance for long PEM scalar values.

If a regression affects only mutable formats, expect failures in the SDMF/MDMF cases while paired CHK cases for the same convergence/length still pass. If a regression affects segmentation or share encoding, failures should cluster around `131071`, `131073`, `2097151`, `2097153`, `8388607`, and `8388609`.
