# `sources/test-tools/fio/.github/actions/build-qemu/action.yml`

Purpose: Composite GitHub Action that installs dependencies, builds QEMU from source, installs it, and removes build artifacts for fio VM-based tests.

Important APIs and inputs: Input `version` defaults to `9.1.0`. Steps install Ubuntu build dependencies, download `qemu-$INPUT_VER.tar.xz`, configure QEMU with KVM and `x86_64-softmmu`, build with `make -j $(nproc)`, run `sudo make install`, and delete the source directory.

Control flow: Called by the QEMU workflow before starting guest VMs. The action uses bash and `INPUT_VER` derived from `${{ inputs.version }}`.

State and persistence: Installs QEMU into the GitHub runner system path and temporarily consumes disk for source/build trees. It removes the source tree afterward but leaves installed binaries for later workflow steps.

Dependencies and integration: Depends on Ubuntu runners, apt packages, network access to `download.qemu.org`, `sudo`, build tools, KVM availability, and the caller workflow.

Risks and test signals: The action file has a misspelled `desription` key, harmless for execution but metadata quality risk. Building QEMU from source is time- and disk-heavy and can fail on upstream URL or package changes. Tests should execute the QEMU workflow, check installed `qemu-system-x86_64`, and monitor runner disk use.
