<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/hdfs.rs -->
# sources/storage-engines/tikv/components/external_storage/src/hdfs.rs

Purpose: this module implements an export-only `ExternalStorage` backend for HDFS by spawning the Hadoop `hdfs dfs -put` command and streaming data into its stdin.

Important APIs and types: `HdfsConfig` holds optional `hadoop_home` and `linux_user`. `HdfsStorage::new` parses and normalizes a remote HDFS URL to a trailing slash. `get_hadoop_home`, `get_linux_user`, and `get_hdfs_bin` resolve command configuration from explicit config or environment variables. `try_convert_to_path` converts hostless `hdfs:///path` URLs to plain `/path` for the HDFS CLI.

Control flow: `write` rejects names containing the platform path separator, resolves the HDFS binary from `$HADOOP_HOME` or config, joins the remote base URL with the object name, builds an optional `sudo -u <user>` command prefix, spawns the process with piped stdin/stdout/stderr, copies the async reader into stdin, waits for command completion, and returns an error with logged stdout/stderr if the command exits non-zero.

State and persistence behavior: successful `write` persists the object in HDFS through the external CLI. The backend does not support reads, ranged reads, listing, or delete; those methods are either `unimplemented!` or return `crate::unimplemented()`.

Dependencies and integration points: it depends on `tokio::process::Command`, `tokio::io::copy`, `url::Url`, and the `ExternalStorage` trait. It is selected by `create_backend` when a BR `Hdfs` backend is supplied.

Risks: read methods panic via `unimplemented!`, unlike `iter_prefix` and `delete`, which return unsupported errors. This makes HDFS unsafe for restore/load paths that call `read`. Command invocation depends on local Hadoop installation, environment, and optional sudo behavior. Name validation rejects nested paths for HDFS, unlike local storage.

Test signals: tests cover `get_hdfs_bin` environment/config resolution and `try_convert_to_path` behavior. There is no integration test that runs a real HDFS command.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/hdfs.rs -->
