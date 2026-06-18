# sources/object-store/openstack-swift/swift/cli/__init__.py

Purpose: package marker for Swift command-line tools. The file is empty and exports no runtime APIs.

Important APIs/types/functions: none. Its significance is structural: it allows modules under `swift.cli` to be imported by console-script entry points and by other modules, such as `swift.cli.get_nodes` importing helpers from `swift.cli.info`.

Control flow: none.

State and persistence: none.

Dependencies and integration: participates in Python package discovery for operational commands including recon, info, dispersion, account auditing, shard-range management, and process tools.

Risks and test signals: operational risk is limited to packaging. Tests or packaging checks should verify `swift.cli.*` imports and console entry points resolve when installed.
