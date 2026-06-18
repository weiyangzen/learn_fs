## sources/user-network-fs/blobfuse2/docker/config.yaml

Purpose: Sample container configuration for mounting Azure Blob Storage with blobfuse2.

Important content: Enables `allow-other`, syslog logging, and the component chain `libfuse`, `file_cache`, `attr_cache`, `azstorage`. `libfuse` cache expirations are set for attributes, entries, and negative entries. `file_cache` uses `/tmp/blobfuse_temp`, disables timeout eviction with `timeout-sec: 0`, permits non-empty temp path, and cleans on start. `attr_cache` timeout is 7200 seconds.

State and dependencies: Runtime state is in `/tmp/blobfuse_temp` and whatever Azure storage config is supplied through environment variables or other mechanisms. It depends on the Dockerfile's directories and FUSE setup.

Risks: This is not a complete standalone config because Azure account/container credentials are absent. `allow-non-empty-temp` and `cleanup-on-start` can delete cached data on container start. Long attr cache timeout may hide remote changes. No direct tests; exercised by container mount workflow.
