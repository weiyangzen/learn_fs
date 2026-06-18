# sources/user-network-fs/rclone/bin/build-xgo-cgofuse.sh

Purpose: tiny release/build helper that builds and pushes a Docker image named `rclone/xgo-cgofuse` from the upstream `winfsp/cgofuse` GitHub repository. It runs `docker build`, lists images, then pushes the image.

State changes are Docker-local image cache mutations and a remote registry push. Dependencies are Docker, network access, permissions to push `rclone/xgo-cgofuse`, and availability of the GitHub Docker build context. Risks include building an unpinned remote repository state, pushing over an existing tag, and no validation beyond Docker command success. There is no test signal in the repo.
