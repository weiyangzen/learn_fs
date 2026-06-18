# sources/storage-engines/tikv/components/encryption/export/examples/ecli.rs

Purpose: `ecli` is an example command-line program demonstrating encryption and decryption of files through KMS-backed `encryption_export` backends.

Important APIs and types: It defines `Operation::{Encrypt,Decrypt}`, `Opt`, `Command::{Aws,Azure,Gcp}`, and provider-specific subcommand structs with `structopt`. Helper functions `create_aws_backend`, `create_azure_backend`, `create_gcp_backend`, `process`, and `main` build backends and transform file content.

Control flow: `process` parses CLI args, reads the input file, builds the selected backend, encrypts plaintext into serialized `EncryptedContent` or decrypts serialized `EncryptedContent` into plaintext, then writes the output file. `main` prints `done` or an error string.

State and persistence behavior: It reads one input path and writes one output path. Credential files are optionally parsed as INI mainly for presence/shape validation. Encryption metadata is persisted as protobuf bytes.

Dependencies and integration points: It uses provider constants, `KmsConfig`, `KmsBackend`, `create_cloud_backend`, `file_system` abstractions, `kvproto::EncryptedContent`, `protobuf::Message`, and `structopt`.

Risks: The Azure helper populates a local `azure_cfg` but never assigns it into `config.azure`, so Azure backend creation appears likely to fail the sanity check in `create_cloud_backend`. The AWS credential parser does not apply credentials to config. Output files are opened with create/write but not truncate, which can leave trailing bytes when overwriting longer files.

Test signals: No unit tests; compilation and manual CLI runs are the signals.
