# sources/object-store/garage/src/garage/tests/k2v/simple.rs

Purpose: This is the smoke test for the raw K2V API.

Important APIs and types: `test_simple` uses `common::context`, `CustomRequester`, Hyper `PUT`/`GET`, `StatusCode`, `BodyExt`, and an `Accept: application/octet-stream` header.

Control flow: The test creates a bucket, PUTs `Hello, world!` at partition key `root` and sort key `test1`, expects 204 No Content, then GETs the same key as octet-stream, expects 200 OK, collects the body, and compares bytes.

State and persistence behavior: It persists one K2V item and reads it back. It does not inspect causality or index state.

Dependencies and integration points: It validates the minimal path through bucket permissions, K2V endpoint routing, SigV4 signing, item insertion, and item retrieval.

Risks: As a smoke test it does not cover content negotiation, conflicts, tombstones, or error bodies. It assumes immediate read-after-write in the single-node integration instance.

Test signals: 204 on insert, 200 on read, exact body equality.
