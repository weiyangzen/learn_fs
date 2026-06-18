# sources/storage-engines/foundationdb/bindings/ruby/lib/fdb.rb

Purpose: This is the Ruby binding entry point. It enforces API-version selection, loads the FFI implementation, selects the C API version, initializes function bindings, and conditionally loads tuple, directory, legacy, and locality modules.

Important APIs and types: Public module methods are `FDB.is_api_version_selected?`, `FDB.get_api_version`, and `FDB.api_version(version)`. The file uses header version `800` and handles C API error `2203` with a detailed max-supported-version message.

Control flow: `api_version` rejects multiple conflicting selections, versions below 14, and versions above the binding header. It requires `fdbimpl`, calls `FDBC.fdb_select_api_version_impl`, initializes `FDBC`, requires tuple and directory layers, loads `fdbimpl_v609` for versions below 610, and loads locality for versions above 22.

State and persistence behavior: It stores selected API version in class variable `@@chosen_version`. No database persistence occurs, but the chosen version controls all subsequent binding behavior.

Dependencies and integration points: It depends on `fdbimpl.rb`, `fdbtuple.rb`, `fdbdirectory.rb`, optional `fdbimpl_v609.rb`, optional `fdblocality.rb`, and native C API version support.

Risks: API version must be selected before normal use, and changing it later is forbidden. Header-version mismatch with installed client libraries produces startup failures.

Test signals: Ruby tester `UNIT_TESTS` verifies repeated same-version selection succeeds and conflicting selections fail with the expected message.
