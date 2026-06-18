<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/static/js/rclone.js -->
# sources/user-network-fs/rclone/docs/static/js/rclone.js

## Purpose

`rclone.js` is the custom browser behavior layer for rclone.org, replacing Bootstrap/jQuery/Popper interactions with vanilla JavaScript.

## Important APIs, Types, and Functions

It implements navbar collapse, dropdown open/close, mega-menu mobile headers and filtering, header anchor injection, TOC overlay and active-section tracking, scrollable table wrapping with sticky headers/arrows, copy-to-clipboard buttons, and global `on_search`.

## Control Flow

An IIFE registers delegated click handlers, decorates dropdowns and headings, builds TOC maps and an `IntersectionObserver`, wraps overflowing tables by cloning headers and synchronizing scroll positions, injects copy buttons into `pre` blocks, and uses the Clipboard API on copy clicks. `on_search` rewrites the search query to exclude the forum domain.

## State and Persistence Behavior

State is client-side DOM state: `.show`, `.filter-hidden`, `.toc-open`, `.toc-active`, `.visible`, and `.copied` classes plus transient filter input values and scroll positions. Nothing is persisted across page loads.

## Dependencies and Integration Points

It depends on DOM APIs, `closest`, `querySelectorAll`, `IntersectionObserver`, `navigator.clipboard`, CSS classes defined by the docs theme, SVG icon symbols, and a form named `search_form`.

## Risks and Test Signals

Risks include unsupported browser APIs, duplicate wrapping if executed twice, table layout mismatch after fonts/images load, clipboard permission failures, unclosed dropdown states, and missing SVG symbols. Tests should use browser smoke tests for nav/dropdown/search, TOC scrolling, table overflow on mobile, copy buttons, and pages without TOC/tables.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/static/js/rclone.js -->
