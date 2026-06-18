
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSwiftAIOsegments

Purpose: Swift AIO variant that disables rclone's segments container behavior.

Important APIs/types/functions: same SAIO image and remakerings mount as `TestSwiftAIO`, but port `28632` and emitted `use_segments_container=false`.

Control flow: Docker run, config echo, shared lifecycle.

State/persistence: disposable container.

Dependencies/integration: tests Swift backend behavior when large object segments are configured differently.

Risks: same SAIO image/ring fragility and fixed port risk.

Test signals: Swift auth connection and backend tests with `use_segments_container=false`.
