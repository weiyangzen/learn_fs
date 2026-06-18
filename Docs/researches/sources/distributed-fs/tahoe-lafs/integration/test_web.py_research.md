# sources/distributed-fs/tahoe-lafs/integration/test_web.py

## Purpose
Broad black-box WebAPI coverage originally added for Python 3 porting. It validates index endpoints, uploads/downloads, status and operations pages, deep check/repair, storage and introducer pages, directory creation with children, and deterministic directory capabilities when private RSA keys are supplied.

## Important APIs, Types, and Functions
Uses `requests` for blocking HTTP, `util.web_get`/`web_post`/`node_url`, `html5lib` and BeautifulSoup for HTML inspection, `allmydata.uri` for capability parsing, Tahoe RSA helpers (`create_signing_keypair`, `der_string_from_signing_key`), and `derive_mutable_keys`. `DATA_PATH` points at Tahoe test RSA PEM fixtures. `test_directory_deep_check` uses `pytest_twisted.ensureDeferred` and `deferToThread` so blocking HTTP work runs off the reactor.

## Control Flow
The file first verifies root index HTML and JSON. Upload tests POST or PUT file content to `/uri`, parse returned CHK or mutable caps, and fetch by readcap. Status tests upload/download content, parse `/status`, follow upload/download links, and inspect event JSON byte counts. Deep stats and deep check tests create mutable directories, upload files, start operation handles, poll `/operations/<handle>` or returned URLs until completion, and validate JSON/HTML outputs. Storage and introducer tests fetch their web pages and JSON summaries. Directory-construction tests create child metadata JSON and call `mkdir-with-children`. Private-key tests base64-url encode DER RSA private keys and assert the resulting directory cap's writekey/fingerprint, including exact known caps for fixed PEM keys.

## State and Persistence
Creates directories, immutable files, mutable files, operation handles, and upload/download status entries in Alice's node and storage grid. Some tests reconfigure Alice's ZFEC parameters before deep-check. Known private-key tests rely on stable PEM fixture files and deterministic mutable key derivation.

## Dependencies and Integration Points
Integrates Tahoe WebAPI routes `/`, `/uri`, `/status`, `/storage`, `/operations`, helper status, introducer root JSON, mutable directory capabilities, RSA key serialization, and web configuration files such as `node.url`.

## Risks
The file comments explicitly state that many assertions encode historical behavior rather than a coherent WebAPI contract. Polling loops have fixed retry counts. HTML assertions are shallow and may be brittle to presentation changes. Private-key capability tests are intentionally exact and will fail on serialization or derivation changes. Blocking requests require `run_in_thread` or `deferToThread` to keep Twisted process IO alive.

## Test Signals
Signals include 2xx HTTP responses, JSON parseability, exact content round trips, expected capability classes and share counts, operation completion statistics, storage reserved-space value, introducer summary keys, and deterministic RSA-derived directory caps.
