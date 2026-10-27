# AGENTS.md

This file provides guidance to agents when working with code in the Project Tapestry repository.

Use this file as the fast path for orientation, navigation, and local conventions.

## Repository Map

- `README.md` is the top-level overview for contributors and developers.
- `CONTRIBUTING.md` describes our requirements and guidelines for those people who wish to contribute to Project Tapestry.
- `SECURITY.md` describes the project security policy and how to report vulnerabilities and related issues.
- `Makefile` is the main task entry point for setup, tests, formatting, linting, type checking, and local docs serving.
- `.*.mk` (e.g., `.common.mk`, `.console-colors.mk`, `.website.mk`, etc.) are support `make` files read by `Makefile`.
- `pyproject.toml` describes the Python dependencies and provides some configuration settings for them.
- `LICENSES/` contains our preferred licenses, which are described in `CONTRIBUTING.md`.
- `docs/` is the main home for design and technical decision docs.
- `src/tapestry/` is the Python package under active development.
- `src/tests/tapestry` mirrors the `src/tapestry` package structure and holds the test suite.
- `contrib/` is the directory where user contributions reside for new, potential capabilities, experiments, etc.
- `examples/` contains runnable examples and demos.
- `website/` is the GitHub Pages site. It is the user-facing technical website.
- `GITHUB_PAGES.md` describes the website that is published using GitHub Pages.
- `Gemfile` and `Gemfile.lock` are used by Ruby for serving the GitHub Pages website locally.
- `*.local/` (e.g., `tenxdev.local/`) is local workspace material and is intentionally excluded from repo-wide navigation guidance unless a task explicitly says otherwise.

## Where To Look First

- For repo setup and contributor workflow: `README.md` and `CONTRIBUTING.md`
- For local build and verification commands: `Makefile` and `.*.mk`
- For the website structure and pages: `GITHUB_PAGES.md`, `website/index.markdown`, `website/contributing.markdown`, `website/about.markdown`, and any other `website/*.markdown` files
- For project-level design docs and technical direction: `docs/README.md`
- For the current Python implementation surface: `src/tapestry/training/consortium/`
- For the current tests: `src/tests/tapestry/training/consortium/`
- For the current user contributions: `contrib/README.md`

## `docs` Map

- `docs/architecture/` holds the TVA methodology, the phase 1–5 outputs, the architectural options, the ADR index, and the diagram placeholders.
- `docs/architecture/0-tva-methodology.md` is the process overview for the full TVA flow.
- `docs/architecture/1-stakeholder-map.md` through `4-design-goals.md` are the requirements-side TVA phases.
- `docs/architecture/5-architectural-options.md` is the option-space / decision analysis stage.
- `docs/architecture/decisions/` holds the numbered ADRs.
- `docs/architecture/diagrams/` holds diagrams and other images used in the architecture documents.
- `docs/governance/` holds governance design, including the anti-capture principle.
- `docs/work-groups/` holds lifecycle work-group charters (data governance, base training, sovereign alignment, evaluation/certification, security/privacy, infrastructure, deployment, and governance participation).
- `docs/strategic-plan/` holds higher-level execution strategy.
- `docs/reference/` is for reference material (e.g. training-paradigm comparisons, deployment and usage notes) outside the phased TVA chain under `architecture/`.

Start with `docs/README.md` and `docs/architecture/README.md` when you need the top-level doc taxonomy, then jump into the bucket that matches the task.

## Python Package Layout

The Python code is organized around three major subsystems:

- `data/` for data governance and management
- `evaluation/` for evaluating models, including benchmarks
- `training/` for distributed training and tuning
- `infrastructure/` for supporting infrastructure

The only implemented training slice in this snapshot is `training/consortium/`, which contains:

- `coordinator.py` for governed shared-base integration
- `node.py` for sovereign training nodes and participant-owned artifacts
- `policy.py` for quality-floor and anti-capture contribution weighting
- `messages.py` for shared dataclasses
- `model.py` for the tiny demo model

Keep new code aligned with that split. Add tests under the matching `src/tests/tapestry/...` path.

## Working Conventions

- Use Python 3.14 and `uv` for environment management.
- Prefer `make` targets for common tasks:
  - `make one-time-setup`
  - `make tests` or `make unit-tests`
  - `make format`
  - `make lint`
  - `make type-check`
  - `make before-pr`
  - `make view-local`
- The default repo test command is `make tests` / `make unit-tests`, which runs discovery from `src`.
- `pytest` is also configured in `pyproject.toml` and is useful for targeted test runs.
- Keep Python formatting consistent with `black` and the repo line length setting in `pyproject.toml` for `tool.black` formatting.
- Keep lint/type annotations compatible with `ruff`, `pylint`, and `ty`.
- Preserve the website style in `website/`: Markdown pages, Jekyll front matter, and Just the Docs structure.
- When editing documentation, keep the audience technical and contributor-focused rather than promotional.
- When creating or editing Markdown under `docs/`, do not hard-wrap prose paragraphs; use soft wrap and break only for Markdown structure (see `docs/README.md` § Writing conventions).
- For new inline Mermaid diagrams in `architecture/reference` docs, follow the conventions in `docs/architecture/diagrams/README.md` § Inline Mermaid style (TAP-009 for decision/sovereignty flows; `0-tva-methodology.md` for phased process/status diagrams).
- Treat governance documents as load-bearing design constraints, not after-the-fact policy notes.

## Build, Lint, Test Commands

```bash
make one-time-setup          # First-time uv venv + dependency install
make tests                   # Run full test suite (alias: make unit-tests)
make format                  # Run black on src/
make lint                    # Run ruff + pylint on src/
make type-check              # Run ty on src/
make before-pr               # format + lint + type-check + tests for src/ AND contrib/*
make consortium-demo         # Run examples/consortium_training_demo.py
```

**Run a single test or file** — pytest is configured with `testpaths = ["src/tests"]` and `pythonpath = ["src"]`, so run from the repo root:

```bash
# Single test function
uv run pytest src/tests/tapestry/training/consortium/test_policy.py::test_all_below_floor_returns_empty -v

# Single test file
uv run pytest src/tests/tapestry/training/consortium/test_policy.py -v

# With WHICH_TESTS make variable (path relative to src/)
make unit-tests WHICH_TESTS=tests/tapestry/training/consortium/test_policy.py
```

**Watch mode** (requires `fswatch`): append `-watch` to most targets, e.g. `make unit-tests-watch`.

## Code Style

- **Line length**: 120 characters (enforced by `black`, `ruff`, and `pylint` — all three configs set to 120).
- **Target version**: Python 3.14.
- All source files begin with `from __future__ import annotations` to enable deferred annotation evaluation.
- Use `collections.abc` types (e.g., `Sequence`) rather than `typing` equivalents for parameter annotations.
- `ModelState = dict[str, torch.Tensor]` is the canonical type alias; import it from `tapestry.training.consortium.messages` in new code — **not** from `types.py` (that file is a compatibility shim for old imports only).
- Dataclasses use `frozen=True` for all message/result types.
- Enums inherit from `(str, Enum)` to allow string aliases (e.g., `ContributionPolicy(weighting="equal")`).
- `pylint` is run with `--recursive=y --ignore=.venv --ignore-patterns='.*cache.*'`; suppress per-file with inline `# pylint: disable=...` comments (see `node.py` for examples).

## Testing Patterns

- Tests live in `src/tests/tapestry/` mirroring `src/tapestry/` exactly — one test file per source module (e.g., `test_policy.py` ↔ `policy.py`).
- **Hypothesis property-based tests** are used heavily alongside standard pytest. Import strategies from `tests.test_utils.hypothesis.model_strategies` (in `src/tests/test_utils/`), not from `hypothesis` directly, for project-specific generators.
- `pytest.approx` with `abs=1e-9` is the standard for floating-point weight assertions.
- Coverage is run automatically by `make unit-tests` via `coverage run -m pytest` + `coverage report -m`.

## Critical Patterns

- `types.py` in `training/consortium/` re-exports everything from `messages.py` for backward compatibility — prefer importing from `messages.py` in new code.
- The `contrib/` tree has its own isolated `make` context: each contribution directory is invoked with `--include-dir $$dir` so a `.custom.mk` there applies only to that subdirectory. Do not assume top-level `make` targets cover `contrib/` automatically — use `make before-pr` (not `make before-pr-top`).

## Plain English (PRs and issues)

Write so a busy reviewer or contributor can understand the point without decoding jargon. Technical precision belongs *after* a clear opening, not instead of one.

- Prefer short sentences and common words when they still say the same thing (“who controls the data” over “control-plane sovereignty boundary”).
- Define project terms on first use, or link the glossary / ADR — do not assume every reader has the full corpus memorized.
- Avoid stacking abstractions, acronyms, and file paths in the first screen of text.
- Comments on issues and PRs should answer in plain language first; optional detail or links can follow.

This applies especially to **issue bodies**, **issue comments**, **PR titles**, and **PR description openings**.

## Pull Request Descriptions

Write PR titles and bodies for human skimming first. Detail is welcome later; the opening must stand alone in plain English.

**Title.** Outcome-oriented and specific enough to understand without opening the PR (e.g. `Add TAP-009: goal-derived base model selection`, not a file-list or implementation diary).

**Opening (fixed order, plain English).** Put this at the top of the description — before file inventories, commit archaeology, or deep rationale:

1. **Why** — the problem or gap this PR addresses.
2. **What** — the proposed approach and what reviewers, users, or the project get when it lands (the result, not the mechanism).

A reviewer who reads only the title and these two beats should understand the forest. If those two beats need a glossary to parse, rewrite them.

**How (details after).** Implementation notes, files touched, edge cases, test evidence, and checklist items come next. Density is fine here.

- When a structural overview helps, **precede the detailed how** with one high-level Mermaid diagram in the recommended style (`docs/architecture/diagrams/README.md` § Inline Mermaid style). Use it for flows, phase shifts, or decision structure — not for typo fixes or pure prose polish.
- At most one diagram in that leading-how position; further diagrams belong deeper in the details if needed.
- Prefer project language over repo archaeology in the opening (“propose a gate-then-score selection method” rather than “updated `classDef` in README”).

Keep using the repo PR templates under `.github/PULL_REQUEST_TEMPLATE/` for checklists and contribution process; lead their description sections with Why → What as above.

## Issue titles and bodies

Same skimming bar as PRs: a reader should know the ask from the title plus the first short paragraph.

**Title.** Name the outcome or question, not the internal ticket shape (e.g. `Pick base model for the #70 two-node experiment`, not `Task/Feature/Issue follow-up`).

**Body opening.** In plain English, state:

1. **Why this exists** — the gap, risk, or decision needed.
2. **What success looks like** — a concrete done condition, decision, or artifact.

Then add background, acceptance criteria, links to ADRs/issues, and checklists. Template fields under `.github/ISSUE_TEMPLATE/` still apply; fill them in readable prose, not telegram-style jargon.

**Comments.** Prefer a clear recommendation or question in the first sentences. Long analysis is welcome after that. When comparing options, say what each option *does for the project* before naming tools or stacks.

## Practical Notes

- Match tests to the package layout instead of creating a separate test structure.
- Avoid broad refactors unless they are required to keep boundaries clear.
- Prefer small, focused changes that stay inside the subsystem you are touching.
- Treat `docs/` as the first stop for architecture, requirements, and design context.
- For repo-wide navigation, ignore `*.local/` directories (e.g., `tenxdev.local/`) unless the task specifically asks for it.
