# sources/sync-backup/git-lfs/script/distro-tool

Purpose: command-line wrapper for distro metadata, implemented as the same Ruby source as `script/lib/distro.rb`.

Important APIs/classes: `DistroMap`, `DistroMapProgram`, `--image-names`, and `--distro-markdown`.

Control flow: builds a distro map, parses exactly one mode option, and either prints Docker image names or PackageCloud download markdown for each supported distro.

State/persistence behavior: read-only, no persistent state.

Dependencies/integration: invoked by release scripts such as `script/upload` to populate package links in GitHub release notes and by packaging jobs to enumerate build images.

Risks: hard-coded distro lifecycle metadata must be kept current. The tool returns status 2 when no mode is specified.

Test signals: `script/spec/distro_spec.rb` exercises image output, markdown formatting, missing-mode errors, and map-derived distro names.
