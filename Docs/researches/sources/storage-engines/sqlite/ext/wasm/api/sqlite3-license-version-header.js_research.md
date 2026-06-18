# sources/storage-engines/sqlite/ext/wasm/api/sqlite3-license-version-header.js

## Purpose
This small preserved header documents licensing for the generated SQLite WebAssembly/JavaScript bundle, typically distributed as `sqlite3.js` or `sqlite3.mjs`. It is intended to survive minification or bundling via `/* @preserve */`.

## Important APIs, Types, and Functions
There are no executable APIs, types, functions, exports, or imports. The file is a comment-only source fragment.

## Control Flow
No runtime control flow exists. During amalgamation/build, the header is prepended to or included in the generated JS bundle so downstream users see the combined licensing notice.

## State and Persistence Behavior
The file holds no runtime state and performs no persistence. Its only durable effect is textual: it records that the bundle combines Emscripten glue code under MIT and University of Illinois/NCSA terms with SQLite-originated code/documentation under SQLite's public-domain-style terms.

## Dependencies and Integration Points
The integration point is the build/amalgamation pipeline for SQLite's WASM JS deliverables. The `@preserve` marker is relevant to minifiers or bundlers that honor preservation comments.

## Risks and Edge Cases
Because it is comment-only, functional risk is low. The main risk is distribution/compliance drift if build tooling drops the preserved comment, if the bundle content changes without updating the notice, or if downstream packagers strip license comments.

## Test Signals
Build-output tests should assert that minified and non-minified `sqlite3.js`/`sqlite3.mjs` artifacts retain the preserved license header. Source scans can confirm no executable code is introduced into this fragment.
