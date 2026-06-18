
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSwiftAIO

Purpose: starts OpenStack Swift All-In-One for Swift backend integration tests.

Important APIs/types/functions: maps local port `28628` to container 8080 and bind-mounts `TestSwiftAIO.d/remakerings` to create storage policy `Policy-1`. Emits Swift v1 auth config.

Control flow: Docker run, config echo, shared lifecycle through `docker.bash`/`run.bash`.

State/persistence: disposable container; remakerings mutates Swift ring config inside container startup.

Dependencies/integration: `openstackswift/saio` image, remakerings script, Swift backend tests.

Risks: external image and custom ring replacement are fragile. Fixed credentials are test defaults.

Test signals: auth endpoint connection and Swift operations.
