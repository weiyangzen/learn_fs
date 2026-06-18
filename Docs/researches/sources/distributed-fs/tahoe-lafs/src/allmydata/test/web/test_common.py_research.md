# sources/distributed-fs/tahoe-lafs/src/allmydata/test/web/test_common.py

## Purpose
This module tests `allmydata.web.common.render_exception`, including response finishing behavior for successful return values, deferred failures, resource delegation, redirects, unknown return types, `NOT_DONE_YET`, and disconnected requests.

## Important APIs, Types, And Functions
`StaticResource` is a Twisted `Resource` whose decorated `render` method returns a configured object. `RenderExceptionTests` covers exceptions, deferred failures, child resources, unicode, bytes, `DecodedURL`, `None`, `NOT_DONE_YET`, unknown objects, and disconnection handling. It uses `render` from `common_web`, testtools Twisted matchers, BeautifulSoup, `assert_soup_has_tag_with_attributes`, and Twisted `ConnectionDone`.

## Control Flow
The tests render resources through the in-process test renderer and assert the resulting body or deferred state. Exceptions and failed deferreds must render error content. Returning an `IResource` should render that resource. Returning unicode or bytes should finish with encoded/raw data. Returning a `DecodedURL` should render a meta-refresh redirect. Returning `NOT_DONE_YET` should leave the render deferred pending until the request writes and finishes. If the request disconnects before a deferred result arrives, the render should fail with `ConnectionDone` without logging a finish-after-disconnect error.

## State And Persistence
State is per-test in-memory request/resource state. `StaticResource` records the request object for the disconnection test. The module calls `gc.collect` at the end of the disconnected case to flush dangling deferreds/logged-error behavior. No persistent files are used.

## Dependencies And Integration Points
This is a direct integration test for Twisted web resources, Tahoe's render decorator, hyperlink `DecodedURL`, BeautifulSoup HTML parsing, and the Tahoe test request renderer. It protects web resources that rely on returning multiple result shapes from decorated `render` methods.

## Risks And Test Signals
The strongest signals are correct request finishing semantics and error rendering. Risks include decorator behavior changing for Twisted versions, HTML redirect shape changes, and logged-error leakage in the disconnection path. The `NOT_DONE_YET` test is especially important because finishing too early would break streaming or manually-finished resources.
