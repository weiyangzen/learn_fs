# sources/distributed-fs/xrootd/src/XrdSciTokens/test/setup_tests.sh

## Purpose

`setup_tests.sh` starts a privileged CentOS 7 Docker container and runs the SciTokens integration test script inside it.

## Important APIs, Types, And Functions

- Checks `OS_VERSION=7`.
- Runs `docker run --privileged --detach --tty --interactive --env container=docker --volume /sys/fs/cgroup:/sys/fs/cgroup --volume $(pwd):/xrootd-scitokens:rw centos:centos${OS_VERSION} /usr/sbin/init`.
- Finds the container ID from `docker ps | grep centos | awk '{print $1}'`.
- Executes `/xrootd-scitokens/test/test_inside_docker.sh ${OS_VERSION}` inside the container.

## Control Flow

The script is an outer harness. It starts systemd-capable Docker, prints logs, runs the inner setup/test script, and lists containers. Stop/remove commands are commented out.

## State And Persistence

It creates a privileged Docker container and bind-mounts the repository read-write. Because cleanup is commented, containers may remain after the run.

## Dependencies And Integration Points

It depends on Docker, CentOS 7 images, systemd-in-container support, and the inner test script. It assumes the current directory is the xrootd-scitokens source root expected by paths in the container.

## Risks And Edge Cases

- Privileged Docker with `/sys/fs/cgroup` mount has high host impact and may not work in restricted CI.
- Container selection via `grep centos` can pick the wrong container.
- No cleanup by default can leak containers and disk.
- Only `OS_VERSION=7` is supported; other values silently do nothing.

## Test Signals

Successful run prints the inner script completion marker and exits zero. Failure signals include Docker startup failure, package install failure, RPM build failure, service restart failure, or token request mismatches.
