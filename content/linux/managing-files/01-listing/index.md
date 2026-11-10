---
title: "Topic 1: Listing files and directories"
date: 2026-11-10
draft: false
weight: 1
summary: "The three ls options I use the most: -l, -a and -lrt, which puts the newest file right above your prompt."
---

`ls` with no arguments shows the contents of the current directory. The three options I use the most:

| Option | Does |
|---|---|
| `ls -l` | **l**ong listing: permissions, owner, size, date |
| `ls -a` | **a**ll files, including hidden ones (names starting with a dot) |
| `ls -lrt` | long listing, sorted by **t**ime, **r**eversed, so the **newest file is last** |

```console
$ ls -lrt old mid new
-rw-r--r-- 1 y.akhras 1049089 0 Jan  1  2026 old
-rw-r--r-- 1 y.akhras 1049089 0 Jun  1 00:00 mid
-rw-r--r-- 1 y.akhras 1049089 0 Nov  4 17:33 new
```

`ls -lrt` is great after you've changed something: the file you just touched is at the bottom, right above your prompt. (The odd group number is because I tested in Git Bash on Windows. On RHEL you see a group name.)

{{< lesson-nav >}}
