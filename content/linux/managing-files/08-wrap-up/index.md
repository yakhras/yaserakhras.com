---
title: "Wrap-up: the -r rule and a cheat sheet"
date: 2026-11-10
draft: false
weight: 8
ShowToc: true
TocOpen: false
summary: "Which commands need -r for a directory and which don't, and a cheat sheet of every command in this tutorial."
---

## ⚠ Attention: which commands need `-r` for directories?

While writing these topics I noticed that some commands need `-r` to work with a directory, and others don't. `-r` means **recursive**: "go inside the directory and handle everything in it, level by level".

> **Need `-r`:** `cp` and `rm`
>
> **Don't need it:** `mv`, `rmdir` and `ls`

| Command | With a directory | Why |
|---|---|---|
| `cp` | **needs `-r`** (or `-a`, which includes it) | it must copy every file inside, one by one |
| `rm` | **needs `-r`** | it must delete every file inside, one by one |
| `mv` | no `-r` | it moves the directory as **one** item, the content goes with it |
| `rmdir` | no `-r` | it removes **only empty** directories, so there is nothing inside to handle |
| `ls` | no `-r` | it lists one directory. With **`-R`** (capital) it also lists every sub-directory |

Without `-r`, `cp` and `rm` refuse a directory:

```console
$ cp somedir newcopy
cp: -r not specified; omitting directory 'somedir'

$ rm somedir
rm: cannot remove 'somedir': Is a directory
```

`mv` doesn't need it. The whole directory moves, with its content:

```console
$ mv somedir moved
$ ls -R moved
moved:
notes
sub

moved/sub:
```

Watch the letter case too: `cp` and `rm` accept `-r` (and `-R`), but for `ls`, `-r` means **reverse order** (like in `ls -lrt`) and only **`-R`** means recursive. There's no logic to it, you just learn them.

## Cheat sheet

| Goal | Command |
|---|---|
| All files, including hidden | `ls -a` |
| Newest file at the bottom | `ls -lrt` |
| Where am I? | `pwd` |
| Copy a file into a directory, safely | `cp file dir/` |
| Copy a directory with everything in it | `cp -r dir target/` |
| Exact copy, keeping permissions | `cp -a dir target/` |
| Copy only the content, hidden files too | `cp -a dir/. .` |
| Move or rename | `mv old new` |
| Delete a directory with its content, for ever | `rm -rf dir` |
| Files with one unknown letter | `ls c?t` |

---

*Based on: Red Hat RHCSA 10 Cert Guide, Chapter 3. The questions are the ones I wrote in the margins while reading, the explanations are my own, and every command was run with the output shown.*

{{< lesson-nav >}}
