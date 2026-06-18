# sources/object-store/garage/src/k2v-client/bin/k2v-cli.rs

Purpose: This file implements the `k2v-cli` command-line utility on top of the `k2v-client` library. It supports inserting, reading, polling, deleting, indexing, range reading, and range deletion with human or JSON output.

Important APIs and types: `Args` holds region, endpoint, key ID, secret, bucket, and `Command`. `Command` variants are `Insert`, `Read`, `PollItem`, `PollRange`, `Delete`, `ReadIndex`, `ReadRange`, and `DeleteRange`. Helpers include `Value`, `ReadOutputKind`, `BatchOutputKind`, `Filter`, `main`, and `run`.

Control flow: `main` sets a default `RUST_LOG`, initializes tracing subscriber, parses clap args, constructs `K2vClientConfig` and `K2vClient`, creates a current-thread Tokio runtime, and runs command dispatch. `Value::to_data` reads text, base64, file, or stdin. Output helpers either print JSON, raw bytes, base64, human text, or table output and then call `exit`. `run` maps each CLI command to the corresponding client call and validates unsupported filter combinations for poll-range/read-index/delete-range.

State and persistence behavior: The CLI persists data only through remote K2V operations. Local state includes parsed args, input file/stdin bytes, and formatted output. It can exit with distinct raw-output error codes for conflict/tombstone cases.

Dependencies and integration points: It depends on `clap`, `tokio`, `tracing-subscriber`, `format_table`, `base64`, and the `k2v-client` public API. Environment variables `AWS_REGION`, `K2V_ENDPOINT`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `K2V_BUCKET` can supply connection options.

Risks: The displayed code constructs a `client` in `main` but `run(args)` as shown does not receive it, while `run` references `client`; this suggests either a compile issue in this snapshot or reliance on missing context not present in the file. Output helpers use `exit`, making them hard to unit test. Error strings contain misspellings like `conlicts-only`. Raw mode refuses concurrent/tombstone results.

Test signals: No direct CLI integration tests are in this group. Library behavior is tested through `garage/tests/k2v_client/simple.rs`; CLI compileability would be covered only by building with the `cli` feature.
