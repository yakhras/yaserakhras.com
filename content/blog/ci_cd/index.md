---
title: "CI/CD in One Picture: My Reading Notes"
date: 2026-10-16
draft: false
tags: ["DevOps", "CI/CD", "DevSecOps", "Learning notes"]
summary: "What I took away from Red Hat's \"What is CI/CD?\": the pipeline, why it matters, and what I'm learning next."
---

I read Red Hat's article [What is CI/CD?](https://www.redhat.com/en/topics/devops/what-is-ci-cd) with a highlighter in hand. These are the ideas I kept, in my own words.

![CI/CD in one picture](infographic_linkedin.png)

## The pipeline: three stages, three places

The way I picture it, each stage runs somewhere different:

| Stage | What happens | Where |
|---|---|---|
| **Continuous Integration** | Build → Test → Merge | in the IDE |
| **Continuous Delivery** | Validated code is released to the repository automatically | on GitHub |
| **Continuous Deployment** | Released code goes to production automatically | in Production |

Red Hat calls these connected practices the **CI/CD pipeline**.

## Why it matters

As apps grow larger, working without CI/CD means more bugs and code failures. CI/CD helps to "decrease complexity, increase efficiency, and streamline workflows". In practice that means:

- code goes from commit to production automatically,
- downtime is kept to a minimum,
- releases happen faster,
- user feedback gets built in sooner and more often,
- and in the end, customers are happier.

## CI vs. "merge day"

Without CI, teams often merge every branch together on a single "merge day", which is slow, manual work that breaks easily. CI replaces that with frequent merges to one shared branch. Every merge triggers automated tests, usually **unit and integration tests**, to make sure nothing broke.

My takeaway: **with CI in place, working on many branches is healthy**, not a risk.

## The two CDs: delivery vs. deployment

- **Continuous delivery** keeps the codebase *always ready* to deploy. A person still decides when it goes to production.
- **Continuous deployment** removes that manual gate. A change "could go live within minutes of writing it (assuming it passes automated testing)."

So deployment is only as safe as your test automation.

## From DevOps to DevSecOps

DevOps and CI/CD share one goal: getting an idea from development into production faster. DevSecOps adds that security is a shared responsibility from start to finish, and its core is a **secure CI/CD pipeline**. Shift-left and shift-right security checks help protect code, prevent data leaks and keep you compliant. Platform engineering builds on DevOps to scale all of this across teams.

## What's next for me

Every stage above depends on good tests. My note in the margin says it plainly: *"We need to learn more about Test."* Unit and integration testing is my next topic.

---

*Source: Red Hat, ["What is CI/CD?"](https://www.redhat.com/en/topics/devops/what-is-ci-cd), updated June 10, 2025. Quotes are short excerpts; the rest is my summary.*
