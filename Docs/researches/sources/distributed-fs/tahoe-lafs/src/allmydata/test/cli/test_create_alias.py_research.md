# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_create_alias.py

## Purpose
This module tests `create-alias`, `add-alias`, alias persistence, alias validation, `webopen` URL construction, and Unicode alias/filename interoperability.

## Important APIs, Types, and Functions
- `CreateAlias._test_webopen` builds `runner.Options`, parses `webopen` with a test client directory, captures streams, and injects `urls.append` instead of opening a browser.
- `test_create` covers alias creation, duplicate rejection, manual alias file newline repair, invalid alias names, and web URLs for root, alias, subdir, file, and info modes.
- `test_create_unicode` covers non-ASCII aliases and remote filenames through `put`, `ls`, and `get`.

## Control Flow
The main test creates a grid, runs `create-alias`, loads aliases from `private/aliases`, creates a second alias, computes expected web URLs from `node.url`, and verifies duplicate create/add behavior. It then loops over invalid alias strings for both `create-alias` and `add-alias`. Webopen checks are synchronous calls into `cli.webopen` with parsed options. The newline-corruption regressions manually strip the trailing newline from the alias file before adding more aliases.

## State and Persistence Behavior
The central persistent artifact is the client directory's `private/aliases` file. Tests verify entries are not overwritten, duplicated, or concatenated after manual newline removal. The module also reads `node.url` and stores generated directory caps. Unicode tests persist alias entries keyed by Unicode names and remote files under those aliases.

## Dependencies and Integration Points
Dependencies include `fileutil`, `get_aliases`, `cli`, `runner`, `GridTestMixin`, `CLITestMixin`, `quote_output_u`, and URL quoting. It integrates alias persistence with web URL generation and with other CLI commands that resolve aliases.

## Risks and Edge Cases
Important risks are corrupting a manually edited aliases file, accepting malformed aliases containing spaces/colons, duplicate alias replacement, incorrect URL quoting for caps and subpaths, and Unicode alias encoding. The webopen tests intentionally preserve even questionable user paths, such as a file path ending in `/`, because that is the CLI contract.

## Test Signals
The tests check both user-visible output and underlying alias map contents. Unicode flow does full write/list/read round-trips. The main residual gap is `list-aliases` Unicode behavior, explicitly left as a TODO in the source.
