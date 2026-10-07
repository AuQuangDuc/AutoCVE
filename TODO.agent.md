# AutoCVE Vietnamese Localization Plan

Starting state: `main` tracks `origin/main`; worktree was clean before this localization effort. No prior persisted modification handoff or active plan existed.

- [x] Task 1 — Establish Vietnamese-first i18n foundation without regressing English/Chinese support
  - Acceptance: `vi`, `en`, `zh` are supported; first load defaults to Vietnamese; persisted language selection still works; language control can select all three locales; existing routes/dashboard translations remain functional.
  - Affected paths: `frontend/src/shared/i18n/**`, `frontend/src/components/layout/LanguageSwitcher.tsx`, app bootstrap/layout as needed.
  - Preserve: existing `autocve.language` storage key, English/Chinese translations, routing and non-localization behavior.
  - Risks: breaking current toggle assumptions, fallback loops, untranslated hard-coded UI appearing after default changes.
  - Phase 2 — AUDIT: inspect i18n bootstrap/resources, language switcher, where i18n is mounted, and existing tests/usages. Evidence: prior grep/read showed only `zh|en`, default/fallback `zh`, two-way switcher, and limited `t(...)` adoption.
  - Phase 3 — IMPLEMENT: implemented `vi|en|zh`, Vietnamese default/fallback, explicit i18n bootstrap, and three-language dropdown while preserving `autocve.language`.
  - Phase 4 — REVIEW/VERIFY: re-read i18n bootstrap/resources/switcher integration. Verification evidence: targeted Biome lint passed for i18n/app/switcher files; `tsc --noEmit` passed; final Vite production build passed. Node 20 was found at `/workspace/ARTEX/.agent-node20/bin`; npm dependencies were installed using workspace-backed TMP/cache because host `/tmp` was full. Acceptance satisfied: `vi|en|zh`, Vietnamese default/fallback, persisted `autocve.language`, three-language selector.

- [x] Task 2 — Localize all frontend user-facing product text into Vietnamese through maintainable i18n usage
  - Depends on: Task 1.
  - Acceptance: core workflows (auth, navigation, projects, tasks, Agent Audit, Direct Audit, Audit Session, One-Click CVE, vulnerabilities, reports, skills, settings/database/checkmarx) show Vietnamese on `vi`, including dialogs/toasts/errors/empty states; dynamic values remain intact.
  - Affected paths: `frontend/src/pages/**`, `frontend/src/components/**`, `frontend/src/app/routes.tsx`, supporting frontend utilities/constants where text reaches UI.
  - Preserve: technical identifiers/acronyms (`CVE`, `RCE`, `SSRF`, `IDOR`, `XSS`, `PoC`, `Agent`, `Finding`, `Skill`, provider/tool names), source data supplied by audited projects, and UI behavior.
  - Risks: broad surface, interpolation mistakes, translating internal/debug strings unnecessarily, breaking tests that assert exact labels.
  - Phase 2 — AUDIT: inventory completed for core workflows; frontend contains many legacy hard-coded Chinese strings plus comments/tests. Existing Chinese→English compatibility map covers a large subset, so Vietnamese compatibility translation is being extended for exact text, attributes, and dynamic templates while semantic `t(...)` remains the primary path for modern screens.
  - Phase 3 — IMPLEMENT: mounted locale-aware legacy DOM translation and added Vietnamese semantic + compatibility mappings covering auth, projects, tasks, Agent Audit/Direct Audit, Audit Session, One-click CVE, vulnerabilities, reports, skills, settings/database/checkmarx and supporting dialogs/utilities.
  - Phase 4 — REVIEW/VERIFY: TypeScript-AST coverage audit found 12 remaining Chinese-containing literals, all inside `pages/prompt-manager/testCodeSamples.ts` sample source-code fixtures rather than UI chrome; all other discovered frontend user-facing literals are covered by curated semantic resources or the generated Vietnamese compatibility fallback. `ReportExportDialog` now emits `vi-VN`/`lang="vi"` metadata. Targeted Biome lint, `tsc --noEmit`, and final Vite production build all passed.

- [x] Task 3 — Localize backend/API/SSE messages that are surfaced to users
  - Depends on: Task 2 for client expectations.
  - Acceptance: authentication, project/task/config/database/embedding/agent endpoints and event payloads used by UI no longer surface Chinese in Vietnamese workflows; internal comments/log-only text can remain unchanged.
  - Affected paths: `backend/app/api/**`, runtime/worker services that emit user-visible messages, related tests.
  - Preserve: API shapes/status codes, machine-readable state keys, compatibility with clients/tests.
  - Risks: exact-message tests, frontend logic that matches Chinese strings, accidental translation of model/tool protocol tokens.
  - Phase 2 — AUDIT: AST scan classified API string literals into returned HTTP/API state versus prompt text, logs and comments. Exact response shapes/status codes/state keys are preserved.
  - Phase 3 — IMPLEMENT: translated authentication, project/task/member, database, embedding, prompt/rule, scan, SSH-key and One-click CVE response/status messages. Re-scanned after detecting and fixing partial-overlap replacements; remaining Chinese API literals are Agent prompts or internal logs.
  - Phase 4 — REVIEW/VERIFY: user-surfaced residual scan over `current_step`, `error_message`, HTTP `detail`, event `message`, tool `error/data` returned no Chinese runtime strings after final cleanup. Python `compileall` and `git diff --check` passed. Targeted Checkmarx/file-tool suite passed 25/25; Agent/One-click regression suite passed 109 selected tests with 2 project-configured deselections.

- [x] Task 4 — Make Agent prompts/runtime output Vietnamese-first while preserving audit semantics
  - Depends on: Tasks 1–3 where displayed runtime language is involved.
  - Acceptance: Direct Audit and relevant Agent/runtime prompts request Vietnamese output; runtime nudge/retry/finalization messages shown to users are Vietnamese; tool names/contracts and finding schema remain unchanged.
  - Affected paths: `backend/app/api/v1/endpoints/agent_direct_audit.py`, `backend/app/services/agent/**`, `backend/app/services/finding_runtime/**`, prompt/skill bindings only where language behavior is explicit.
  - Preserve: vulnerability-quality requirements, source→sink/PoC/confidence rules, terminal tool contract, state-machine behavior.
  - Risks: semantic drift in security prompt, breaking tests that assert prompt fragments or stop messages.
  - Phase 2 — AUDIT: located explicit Chinese-response directives, Finding recovery/finalizer/native-tool prompts, compaction/resume paths, and user-visible Agent/tool messages; inspected exact-text tests before changing contracts.
  - Phase 3 — IMPLEMENT: Direct Audit and Recon/Scan/Triage/Finding/Verification/Orchestrator now instruct Vietnamese-first output; Finding initial/summary messages, recovery/finalization/native-tool prompts, compaction, resume, retries and relevant Agent/tool result messages were localized while preserving tool names, schemas, state keys and terminal behavior.
  - Phase 4 — REVIEW/VERIFY: dedicated Finding Runtime suite passed 109/109 tests after updating expected localized contracts. Agent/One-click suite passed 109 selected tests with the two pre-existing project-configured deselections. Mixed-language AST review leaves only intentional Chinese upstream system prompts paired with Vietnamese response directives; no mixed Chinese/Vietnamese tool string remains.

- [x] Task 5 — Eliminate residual user-facing Chinese and document intentional exceptions
  - Depends on: Tasks 1–4.
  - Acceptance: static scans and representative UI paths find no Chinese user-facing product text in Vietnamese mode; remaining Chinese is limited to comments, fixtures/sample audited content, Chinese locale, or explicitly documented compatibility parsing.
  - Affected paths: repository areas identified by residual scans.
  - Preserve: upstream Chinese locale and any parser patterns required to understand legacy persisted/error content.
  - Risks: false positives from comments/tests, false negatives in dynamic strings returned from backend.
  - Phase 2 — AUDIT: repeated TypeScript-AST and backend surfaced-string scans across frontend/backend; reviewed mixed-language string constants separately to catch partial replacements.
  - Phase 3 — IMPLEMENT: filled remaining frontend fallback coverage, localized demo data/report export/Checkmarx headers, One-click/Agent/tool/knowledge outputs, and cleaned mixed Chinese–Vietnamese tool strings found during diff review.
  - Phase 4 — REVIEW/VERIFY: frontend audit now reports only 12 Chinese-containing literals, all deliberate sample source-code fixtures in `testCodeSamples.ts`. Backend scan of surfaced `current_step`/`error_message`/HTTP `detail`/event `message`/tool `error`/`data` returns no Chinese runtime strings. Intentional exceptions: `zh` locale keys/values, comments/log-only text, Chinese sample source fixtures, compatibility parsers/error classifiers, and upstream Chinese system-prompt bodies that explicitly direct Vietnamese responses.

- [ ] Task 6 — Final integration review and regression verification
  - Depends on: Tasks 1–5.
  - Acceptance: combined final diff preserves behavior; frontend type/lint/test/build pass; applicable backend targeted/regression tests pass; Docker Compose configuration/build validation is performed with available project tooling; no live process remains.
  - Affected paths: final repository state only; no unrelated cleanup.
  - Risks: later localization edits invalidating earlier tests, build-only missing imports/keys, Docker/environment limits.
  - Phase 2 — AUDIT: review complete diff against starting worktree and dependency interactions.
  - Phase 3 — IMPLEMENT: only fixes discovered by integration review/checks.
  - Phase 4 — REVIEW/VERIFY: rerun invalidated checks, build/smoke validation, `git diff --check`, final status and residual limitations.

- [x] Task 7 — Publish Vietnamese default README while preserving original language editions
  - Depends on: existing localized UI scope (Tasks 1–5); does not require unresolved Docker validation in Task 6.
  - Acceptance: `README.md` is readable Vietnamese covering upstream functionality, workflows, security and license; Chinese source is preserved byte-for-byte as `README_ZH.md`; `README_EN.md` content stays intact except language navigation; links to all three versions work.
  - Affected paths: `README.md`, new `README_ZH.md`, `README_EN.md`.
  - Preserve: all original CVE references/numbers and source attributions, logo/media URLs, security constraints, badge/license links and unchanged external facts.
  - Risks: broken Markdown anchors/internal links; claiming upstream release contains unshipped Vietnamese UI; accidental loss of original Chinese README information.
  - Phase 2 — AUDIT: read both original READMEs, local Compose/production Compose, versioned deployment URLs and documentation tree. Existing 30-row CVE table, upstream release image pins, and current local source-build differences identified.
  - Phase 3 — IMPLEMENT: wrote Vietnamese default README preserving the upstream capabilities, 30-row CVE table and security/license/contact context; copied original Chinese README to `README_ZH.md`; changed only the language navigation in `README_EN.md`.
  - Phase 4 — REVIEW/VERIFY: `git show HEAD:README.md | cmp - README_ZH.md` passed byte-for-byte; 30 CVE identifiers/order unchanged; English README equals HEAD aside from language links; local documentation/images and code fences checked; `git diff --check -- README.md README_EN.md` passed. Task 8 is responsible for expanding validated operational guidance.

- [x] Task 8 — Add verified Vietnamese operational guidance for setup, models, audit and troubleshooting
  - Depends on: Task 7.
  - Acceptance: Vietnamese README explains requirements, local Docker build, upstream image caveat, service access, model/API key setup, project import/audit/finding/report workflows, operational commands and security/troubleshooting; executable commands map to project configs.
  - Affected paths: primarily `README.md`; refer to docs/USER_GUIDE_EN.md, docker-compose.yml, backend/env.example and application routes without editing them.
  - Preserve: real variable names, routing, command semantics, internal services and current usage modes.
  - Risks: exposing default demo credentials without warning; confusing prod versus local setup; volume-loss commands, mounting docker.sock, outdated environment examples.
  - Phase 2 — AUDIT: verify guide/Compose/env keys and source UI entry points prior to edits; existing docker-compose.yml serves frontend :3000, API :8000, Swagger :8000/docs, Adminer :8080; prod Compose references upstream v1.0.5 images.
  - Phase 3 — IMPLEMENT: expanded `README.md` with verified environment requirements, local/upstream Docker modes, `backend/.env` configuration and secrets guidance, default demo account warning, model protocol cautions, project/Agent/Finding/report walkthrough, worker diagnostics, operational lifecycle, troubleshooting and Docker socket/database exposure warnings.
  - Phase 4 — REVIEW/VERIFY: cross-checked env keys against `backend/app/core/config.py` and `backend/env.example`; verified routes, Compose service names/ports and `/health` against repository; verified demo account in `backend/app/db/init_db.py`, production `v1.0.5` image pins; `git diff --check` passed. Commands are text/source-validated only; Docker CLI is unavailable here, so no live deployment claim. Changed env refresh example to explicitly recreate relevant worker/backend containers.

- [x] Task 9 — Final README localization integration verification
  - Depends on: Tasks 7–8; independent of unfinished application runtime/docker validation in Task 6.
  - Acceptance: Vietnamese and English README each offer navigation to all three languages; original Chinese README remains byte-identical to upstream (Vietnamese reachable via English), preserved material and Markdown structures are validated; working tree has no unexpected documentation changes; documentation-only checks pass; unrelated Task 6 limits remain explicit.
  - Affected paths: README editions and `TODO.agent.md` only.
  - Preserve: existing incomplete Task 6 status; unrelated active application localization changes.
  - Risks: accidental path/case errors, broken images and code fences, unverified Docker commands.
  - Phase 2 — AUDIT: compared all three README editions, language navigation, relative document/media refs, anchors, 30 upstream CVE references, existing route/Compose/env contracts and README cross-references in the repository. Upstream Chinese file intentionally stays byte-identical; navigation from Chinese to Vietnamese is via English README.
  - Phase 3 — IMPLEMENT: removed an unintended Chinese product-language phrase remaining in the Vietnamese note while preserving the Chinese language name in the selector. Adjusted README env refresh command to explicitly force-recreate affected backend/worker containers.
  - Phase 4 — REVIEW/VERIFY: static checks passed for 13/8/7 local references in Vietnamese/English/Chinese editions respectively, four anchors in each, balanced code fences/details/div containers, Vietnamese user-facing text, 30/30 preserved CVE links/order, exact upstream Chinese bytes, unchanged English content apart from language navigation, documented operational keys, and `git diff --check`. No Docker CLI is installed in this project execution environment, so live Docker validation remains an explicitly unexecuted check under pre-existing Task 6 (still unchecked).

