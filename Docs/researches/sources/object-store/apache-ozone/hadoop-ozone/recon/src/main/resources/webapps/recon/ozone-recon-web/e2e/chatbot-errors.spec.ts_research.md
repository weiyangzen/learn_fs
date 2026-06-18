# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/e2e/chatbot-errors.spec.ts

## Purpose

`chatbot-errors.spec.ts` is a Playwright end-to-end test suite for the Recon AI Assistant error and edge-state UI. It verifies disabled/not-configured states, empty state, loading state, successful Markdown rendering, chat error messages for several HTTP failures, and model-fetch fallback behavior.

The suite is network-isolated for chatbot endpoints: each test intercepts `/api/v1/chatbot/health`, `/api/v1/chatbot/models`, and/or `/api/v1/chatbot/chat`, then navigates to `/#/Assistant` and asserts visible UI text or rendered elements.

## Important APIs, Types, and Functions

- `test` and `expect` come from `@playwright/test`.
- `test.describe('Recon AI Error Handling Scenarios', ...)` groups all Assistant scenarios.
- `page.route(... route.fulfill(...))` stubs backend responses.
- `page.goto('/#/Assistant')` loads the hash-routed Assistant page using the configured base URL.
- `page.fill('textarea', ...)` and `page.keyboard.press('Enter')` submit chat messages.
- `expect(page.locator(...)).toBeVisible()` asserts UI state.
- `page.screenshot(...)` writes scenario screenshots under `e2e/screenshots`.

## Control Flow

The suite covers `health-disabled`, `health-not-configured`, `empty-state`, `chat-loading`, `chat-success`, `chat-503-busy`, `chat-504-timeout`, `chat-500-internal`, `chat-503-interrupted`, `chat-503-disabled`, `models-500`, and `models-503`. Each test installs route stubs, loads `/#/Assistant`, performs any needed chat submission, asserts visible output, and captures a screenshot.

The chat success case returns Markdown with a GFM table and expects a rendered `table`. The 500 case expects normalized UI copy plus a server-log hint, while several 503/504 cases expect exact backend-provided messages. Model endpoint failures must still leave the Assistant usable with `Default Provider`.

## State and Persistence Behavior

The tests do not intentionally share state. Playwright provides isolated page fixtures, and route handlers are per page. The UI state under test is transient browser state: health gating, available model/provider state, chat messages, loading state, Markdown rendering, and error rendering.

The only persisted artifacts are screenshots under `e2e/screenshots`, which provide visual evidence but are not the assertion mechanism.

## Dependencies and Integration Points

This suite depends on `@playwright/test`, `playwright.config.ts`, the Vite dev server at port 3000, the hash route `/#/Assistant`, Assistant UI text and selectors, Markdown rendering through `react-markdown`/`remark-gfm`, and the chatbot API response contracts for health, models, and chat. Because chatbot routes are stubbed, it does not require a live LLM provider.

## Risks

Text locators and `.loading-bubble` are sensitive to copy and class changes. The loading test has timing sensitivity because it depends on a delayed response and a transient DOM state. Fixed screenshot paths can leave stale visual evidence if a test aborts before writing. The tests stub chatbot endpoints only, so unrelated page requests can still affect load behavior. Error handling expectations are mixed between exact backend strings and normalized UI copy, so behavior changes need coordinated test updates.

## Test Signals

Run with `pnpm e2e`. Passing tests indicate that health gating, model fallback, chat submission, loading feedback, Markdown table rendering, and key error states are visible in Chromium. Screenshots under `e2e/screenshots` are useful supporting artifacts.
