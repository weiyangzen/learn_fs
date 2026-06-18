# sources/sync-backup/git-lfs/script/lib/distro.rb

Purpose: authoritative Ruby metadata and CLI implementation for supported package distribution targets.

Important APIs/classes: `DistroMap.builtin_map`, `DistroMap#distro_name_map`, `DistroMap#image_names`, `DistroMapProgram#image_names`, `#distro_markdown`, and `#run`.

Control flow: `builtin_map` defines source distro keys with package component, Docker image, package type, package tag, and equivalent PackageCloud distro names. Program mode parsing selects image-name output or markdown link output and returns status 2 for missing mode.

State/persistence behavior: no persistence. Output is deterministic based on insertion order of the map.

Dependencies/integration: used by package upload and release-note generation. `packagecloud.rb` uses `distro_name_map`; `upload` uses markdown output.

Risks: distro equivalents and EOL comments are manual release engineering data. Incorrect package tags/components lead to wrong package URLs or uploads. Markdown uses fixed amd64/x86_64 arch labels.

Test signals: `script/spec/distro_spec.rb` validates program outputs and derived maps against a fixture map.
