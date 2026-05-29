# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 0. Session Start — Read Project Commands

At the start of every session or new project, **scan `.claude/commands/` and read every `.md` file inside** before doing any other work. These files define project-specific rules and slash commands (e.g. `create-prd`, `generate-tasks`, or anything else added later by the team).

Why this matters:

- Knowing the commands lets you **suggest the right one** when the user describes a task that matches (e.g. proposing `/create-prd` when they describe a new feature).
- Knowing the internal rules of each command lets you **follow them automatically** when invoked, without having to re-read mid-flight.
- New commands added by the team get picked up the next session, no extra config needed.

Operationally: this is a one-time scan per session. You don't need to announce the list of commands unprompted — just have them in working memory so you can route the user correctly when they describe their need.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

## 5. Branch per Parent Task

**One Git branch per top-level task. Never mix tasks on the same branch.**

For each parent task in `tasks/tasks-*.md` (e.g. 1.0, 2.0, 3.0…), open a new branch from the project's integration branch BEFORE starting work. Sub-tasks of the same parent share the branch.

### Naming
Examples:
- `task/myarmari-1.0-monorepo-setup`
- `task/myarmari-2.0-backend-service`
- `task/myarmari-3.0-app-shell`
- 
### Lifecycle
1. **Start of parent task**: pull integration branch, create new task branch from it, push to remote
2. **Sub-tasks**: commit and push to the same task branch
3. **End of parent task**: open a PR against the integration branch with a summary of what landed, request review (or self-merge if solo)
4. **After merge**: delete local + remote branch, pull integration branch, then start the next task on a new branch

### Why
- Each task gets its own diff / review surface
- Easy to revert a single task without affecting others
- The PR history is the implementation diary
- Multiple tasks can be paral·lelitzades si calen reviews simultanis

### Exception
PRD task **0.0 "Create feature branch"** is the *first* task branch and follows the same convention.


## 6. Visible question in the thread
 
**Whenever you use `AskUserQuestion`, first write the same question and options as text in the conversation thread before calling the tool.**
 
Why: the `AskUserQuestion` dropdown takes over the screen and covers the previous context. If the user wants to review what you did before answering, they can't. Repeating the question in the thread leaves a permanent copy that survives once they've answered.
 
Minimum format:
- Short title (`##` or **bold**)
- Numbered or bulleted list with each option + 1 line of description
- (Optional) your recommendation + why
Then call `AskUserQuestion`. No need to repeat it word-for-word — the idea is that the user can read it with the question dropdown closed.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
