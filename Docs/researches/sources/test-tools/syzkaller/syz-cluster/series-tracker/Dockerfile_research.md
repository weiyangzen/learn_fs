## sources/test-tools/syzkaller/syz-cluster/series-tracker/Dockerfile

This Dockerfile packages `series-tracker`. It copies the binary from the common builder image into an Ubuntu runtime and installs `git`, which is required for polling lore git archives.

Build args are `IMAGE_PREFIX` and `IMAGE_TAG`. Integration is with the series-tracker deployment and persistent git repository volume. Risks include using `ubuntu:latest`, package update variability, and running as root by default.
