# sources/distributed-fs/tahoe-lafs/src/allmydata/test/web/common.py

## Purpose
This helper module centralizes BeautifulSoup assertions and unknown/future capability fixtures for web tests. It keeps HTML structure checks consistent across root, introducer, status, and grid web test modules.

## Important APIs, Types, And Functions
Constants `unknown_rwcap`, `unknown_rocap`, and `unknown_immcap` are UTF-8 encoded future/unknown caps used by directory and info-page tests. Assertion helpers include `assert_soup_has_favicon`, `assert_soup_has_tag_with_attributes`, `assert_soup_has_tag_with_attributes_and_content`, `_normalized_contents`, `assert_soup_has_tag_with_content`, and `assert_soup_has_text`.

## Control Flow
The helpers search a soup tree for expected tags, attributes, text nodes, or normalized text content and call the provided test case's assertion/failure methods. Attribute matching treats expected values as members of the actual attribute list, which is important for HTML attributes such as `rel`.

## State And Persistence
No mutable state or persistence is used. The module only holds constant future caps and pure assertion helpers.

## Dependencies And Integration Points
It depends on `re` and BeautifulSoup-compatible soup objects supplied by callers. It is imported by web tests for favicon checks, link/tag checks, text checks, and unknown cap coverage.

## Risks And Test Signals
These helpers can hide or expose broad UI regressions. Risks include fuzzy content checks passing when markup changes in unintended ways, attribute matching assumptions that fit list-valued attributes better than scalar attributes, and duplicated typo text in docstrings only. The helpers provide strong signals for expected Tahoe web UI affordances such as favicon and specific rendered text.
