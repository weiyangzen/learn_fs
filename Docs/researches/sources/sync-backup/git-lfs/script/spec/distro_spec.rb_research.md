# sources/sync-backup/git-lfs/script/spec/distro_spec.rb

Purpose: RSpec coverage for distro metadata formatting and derived maps.

Important APIs/functions: `test_map`, `DistroMapProgram#run`, `DistroMap#distro_name_map`, and `DistroMap#image_names`.

Control flow: builds a small fixture map, captures `stdout`/`stderr` with `StringIO`, and asserts `--image-names`, `--distro-markdown`, no-option error status, equivalent distro map, and image list.

State/persistence behavior: no persistence; tests operate entirely in memory.

Dependencies/integration: validates `script/lib/distro.rb`, and indirectly protects `script/upload` release body links and PackageCloud upload mapping.

Risks: fixture data intentionally differs from current builtin data, so tests cover formatting logic rather than current distro support. They assume Ruby hash insertion order.

Test signals: failing expectations indicate output formatting drift or option-handling changes.
