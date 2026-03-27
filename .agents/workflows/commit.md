---
description: Auto-generate a commit message from changes and commit them to a specified or current branch
---

1. Determine the target branch from the user's input (e.g., if the user ran `/commit feature-branch`, the target is `feature-branch`). If no branch is specified, the default target is the current branch.
2. If a target branch was specified and it is different from the current branch, switch to it using `git checkout -b <target_branch>` (if it's a new branch) or `git checkout <target_branch>`.
3. Stage all current modifications with `git add .`
// turbo
4. Retrieve the staged changes by running `git diff --cached`. If there are no changes, notify the user and stop.
5. Analyze the changes and generate a concise, descriptive commit message summarizing what was modified.
6. Commit the changes using `git commit -m "<your_generated_commit_message>"`.
7. Inform the user about the successful commit, including the branch name and the commit message used.
